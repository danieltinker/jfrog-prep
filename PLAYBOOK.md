# Playbook: from "here is a wheel" to "here is the payload"

One method. Seven steps. Do them in order every time, even when you think you already see the
answer. The order is what keeps you calm.

```
0. Safety      do not install it
1. Unpack      it is just an archive
2. Map         list every file, read the metadata
3. Trigger     find WHERE code starts running
4. Sink        find WHERE decoded data gets executed
5. Peel        remove one layer at a time, write each one down
6. Payload     read it, name what it does, collect IOCs
7. Report      2 minutes, structured
```

---

## Step 0 - Safety (say it out loud)

- Never `pip install` the sample. Never `pip download` a source package either: pip may run the
  package's build code just to read its metadata.
- Work in a fresh empty folder. Keep your own scratch scripts in a *different* folder.
- Static first. If you must run something, run **only the decoding lines**, copied into your own
  scratch file, with the execution call swapped for `print`.

## Step 1 - Unpack

| File | What it is | How to open |
|---|---|---|
| `name-1.0-py3-none-any.whl` | Wheel = a **zip** | `unzip sample.whl -d out/` |
| `name-1.0.tar.gz` | Source distribution (sdist) | `tar xzf sample.tar.gz -C out/` |

Take a hash first (`shasum -a 256 sample.whl`). Researchers always record it; it is IOC number one.

## Step 2 - Map the package (2 minutes, no code reading yet)

List everything, with sizes. `find out -type f | xargs ls -la` or just open the folder tree.

A wheel always has two parts:

```
package_name/            <- the code
package_name-1.0.dist-info/
    METADATA             <- name, version, author, homepage, dependencies
    RECORD               <- list of EVERY file that will be installed, with hashes
    WHEEL                <- build tool and tags
    entry_points.txt     <- (optional) command-line scripts it installs
    top_level.txt        <- (optional) importable top-level names
```

Questions to answer from the map alone:

1. **Does the name imitate something?** `requessts`, `colourama`, `python-dateutils`. Is the
   homepage in `METADATA` the real project's repo while the author is someone else?
2. **Is there a file that does not belong?** Read `RECORD` top to bottom. Red flags:
   - a `.pth` file (runs at every Python start),
   - `sitecustomize.py` or `usercustomize.py`,
   - `.pyc` files with no matching `.py`,
   - a top-level module that is not the package (`cook.py` next to `litellm/`),
   - data files with odd names or sizes: `.png`, `.dat`, `.bin`, `.pem`, `.txt`, `LICENSE` that is 300 KB.
3. **Which file is suspiciously big, or suspiciously small?** A 40 KB `_utils.py` in a tiny
   package is where the blob lives.
4. **What does it depend on?** `Requires-Dist` in `METADATA`. A colour library that needs
   `requests`, `cryptography` and `pycryptodome` is odd. The payload can also live in a dependency.

For an sdist the map is: `setup.py`, `setup.cfg`, `pyproject.toml`, `PKG-INFO`, the package folder.
Start with `setup.py`.

## Step 3 - Find the trigger

Malware has to *start*. There are only a few places it can start from. Check them in this order:

| # | Trigger | Where to look | Runs when |
|---|---|---|---|
| 1 | `setup.py` top-level code | sdist only | install / build |
| 2 | `setup.py` custom command class (`cmdclass=`) | sdist only | install / build |
| 3 | `pyproject.toml` custom build backend | sdist only | install / build |
| 4 | `.pth` file - any line starting with `import` | wheel or sdist | **every** Python start |
| 5 | `sitecustomize.py` | wheel | every Python start |
| 6 | `__init__.py` top-level code | both | `import package` |
| 7 | a module that `__init__.py` imports (follow the chain!) | both | `import package` |
| 8 | `entry_points.txt` console script | both | user runs the command |
| 9 | inside one function / class method | both | only when called |

**Follow the import chain.** `__init__.py` looks clean, but it does `from ._compat import *`.
`_compat.py` looks clean, but its last line imports `._win32`. Open every file that gets imported.
Draw the chain in your notes: `__init__ -> _ansi -> _win32 (blob here)`.

Code inside `try: ... except: pass` at module level is a classic tell: the author wants it to fail
silently on machines where it does not work.

## Step 4 - Find the sink

The **sink** is the call that turns data into running code. Everything before it is decoding.
Find the sink first, then walk *backwards* from it. Do not read obfuscated code top to bottom.

Search all files (editor "find in files", or `grep -rn`) for these words:

| Family | Words to search |
|---|---|
| Run a string as code | `exec`  `eval`  `compile` |
| Run a serialized object | `marshal.loads`  `pickle.loads` |
| Hidden lookup of the above | `__import__`  `getattr`  `globals()`  `builtins`  `__builtins__`  `importlib` |
| Run a process | `subprocess`  `os.system`  `os.popen`  `Popen`  `powershell`  `cmd /c`  `bash -c` |
| Decoding | `b64decode`  `b32decode`  `b85decode`  `fromhex`  `unhexlify`  `decompress`  `codecs`  `rot13`  `Fernet`  `AES`  `chr(`  `[::-1]`  `^` |
| Network | `urllib`  `requests`  `http`  `socket`  `webhook`  `telegram`  `discord` |
| Sensitive reads | `os.environ`  `.ssh`  `.aws`  `Login Data`  `Cookies`  `wallet`  `keychain` |

Then three visual checks, because the authors hide from search:

1. **Turn word wrap ON.** A line can hold 300 spaces and then `; <code>`. Without wrap you see a
   harmless short line. Also look at the horizontal scrollbar: if one line is 5,000 characters wide,
   go there.
2. **Sort files by size, and look for the longest line.** The blob is always long.
3. **Names split to dodge search.** `"ex" + "ec"`, `"\x65\x78\x65\x63"`, a list of numbers passed to
   `chr`. If `exec` returns zero hits but there is a `getattr(` or `__import__(` with a computed
   string, that is your sink.

## Step 5 - Peel the layers

Rule: **one layer at a time, and name it before you remove it.**

For each layer:

1. *Look* at the data. What does it look like? (Recognition table in `CHEATSHEET.md`.)
2. *Read* the code around it. The code tells you the exact order of operations - it must, because
   it has to decode it itself. Read the expression **inside-out**: the innermost call happens first.
3. *Remove* that one layer (CyberChef, or a Python REPL).
4. *Look* at the result. Is it readable Python? Then you are done or at a new stage. Is it more
   noise? Then identify the next layer.
5. *Write one line* in your notes: `layer 2: reversed, then Base64`.

Reading inside-out, example. The code says:

```python
run(zlib.decompress(base64.b64decode(data[::-1])))
```

Innermost first: (1) reverse the string, (2) Base64-decode, (3) zlib-decompress. That is your
CyberChef recipe, in that order: **Reverse -> From Base64 -> Zlib Inflate**.

### CyberChef or Python? Decide fast

| Situation | Use |
|---|---|
| Standard encodings, 1-5 layers | CyberChef |
| You do not know what it is | CyberChef "Magic" operation, with a crib if you know one |
| Same layer repeated 20+ times | Python loop |
| Custom decoding function written by the author | Python: **reuse their function** |
| Key depends on something at runtime | Python, after you work out the runtime value |

### The most important trick: reuse their decoder

When the author wrote a custom decrypt function with ugly names, do **not** try to understand the
maths. You do not need to. Do this instead:

1. Create your own `scratch.py` in your scratch folder.
2. Copy into it: the decode function, the data, the key. Nothing else.
3. Where the original passes the result to the sink, write `print(...)` instead.
4. Run `scratch.py`.

You are running *their arithmetic* on *their data*, and nothing else. This is what the hint
"run code to decrypt the payload" means.

Before running, read what you copied and make sure it contains no network, file or process call.
Pure arithmetic on bytes is safe to run.

### When the same wrapper repeats many times

If decoding gives you the same shape again (another call to the same function around another
blob), stop doing it by hand. Write a loop: decode, check whether the result still looks like a
wrapped blob, repeat. Drill 14 trains exactly this.

## Step 6 - Read the payload

You reached readable code. Now answer four questions, quickly:

1. **What does it collect?** files, env vars, browser data, tokens, system info
2. **Where does it send it?** URL, webhook, bot API, raw socket
3. **What does it fetch or run next?** downloads a file, runs a command, starts a process
4. **Does it stay?** startup folder, scheduled task, cron, writes itself somewhere

Common payload families and how to recognise each in ten seconds:

| Family | Tell-tale signs |
|---|---|
| Downloader / dropper | fetches a URL, writes to a temp folder, starts a process |
| Info-stealer | browser profile paths (`Login Data`, `Cookies`, `Local State`), `discord`, wallet names, `.ssh`, `.aws`, `os.environ` |
| Credential / env exfil | reads `os.environ` or config files and POSTs them |
| Remote shell / RAT | a socket or polling loop plus a process call |
| Clipper | reads the clipboard in a loop, regex for wallet addresses |
| Miner | downloads a binary, mentions a pool address, CPU count |

Collect IOCs as you read: every URL, domain, IP, file path, file name, registry key, env-var
marker, user-agent string, hard-coded key. Write them **defanged**.

Is there another encoded string *inside* the payload? Then there is another stage. Typical: a
Base64 argument to PowerShell, a URL stored as numbers, a second blob.

## Step 7 - Report

See the 8-line skeleton in `INTERVIEW.md`. Read it from your notes.

---

# When you are stuck

Find your symptom. Try the fixes in order.

### "I searched for exec/eval and found nothing"

1. Search the *hidden lookup* family: `getattr`, `__import__`, `builtins`, `globals`.
2. Search for string pieces: `"ex"`, `"ev"`, `\x65`, `chr(`.
3. Not in `.py` files at all? Check `.pth`, and every non-Python file.
4. Search for `subprocess` and `os.system`: the code may run a *command* instead of a string.
5. Check `.pyc` files and `Requires-Dist`: the code may be compiled, or in a dependency.

### "I cannot find where it starts"

1. Go back to the trigger table. Did you open **every** imported module?
2. Read `RECORD` again. Is there a file you never opened?
3. Sort by size. Open the biggest and the smallest files you skipped.

### "My decode gives garbage"

1. **Order.** Reread the expression inside-out. Is there a reverse or a slice first?
2. **Whitespace and quotes.** Did you copy the surrounding quotes, a `b'` prefix, or newlines?
3. **Wrong alphabet.** URL-safe Base64 uses `-` and `_`. Base85 has several alphabets.
4. **Missing padding.** Add `=` until the length is a multiple of 4.
5. **It is compressed.** Look at the first bytes after decoding (magic table in the cheatsheet).
6. **It is encrypted.** There must be a key. Find where the code builds it.
7. **The key depends on the environment.** `__name__`, `__file__`, the hostname, the date, an env
   var. `__name__` is `"__main__"` when you run a file directly but `"package.module"` when it is
   imported - so the same code gives a different key in your scratch file. Work out what the value
   would be on a real victim and hard-code that.
8. **Bytes versus text.** In Python, call `.decode()` at the end, or look at the raw bytes.

### "I ran the decoder and nothing printed"

1. **A guard returned early.** Look for checks on the OS (`platform.system()`, `os.name`,
   `sys.platform`), user name, host name, env vars (`CI`, `JENKINS_URL`), date, CPU count, or a
   debugger check (`sys.gettrace`). Do not satisfy the guard - just copy the decoding lines out
   from under it.
2. **An exception was swallowed.** Remove the `try/except` in *your scratch copy* and read the
   real error.
3. **You printed the wrong thing.** Print the type and the first 200 characters:
   `print(type(x), repr(x[:200]))`.

### "The code is unreadable - names like `O0O0OO0` and `lIlIlI`"

1. Do not read it. Find the sink, walk backwards.
2. Rename as you understand: editor "rename symbol", or plain find-and-replace. `O0O0OO00O` ->
   `decrypt`, `llIIllII` -> `key`.
3. Delete what is never used. Half of it is junk on purpose.
4. Then reuse their decoder (Step 5).

### "I am out of time"

Say what you have: the trigger, the layers you removed, what the next layer looks like, and what
you would do next. A clear partial answer beats a silent struggle.

---

# Logging: watching what code does without trusting it

The hint mentioned "logging". Three levels, weakest to strongest. Use them only on the decoding
part, inside the environment the interviewer gives you.

1. **Print in place.** In your scratch copy, put `print(repr(value)[:300])` after each decoding
   step. You see every intermediate layer.
2. **Replace the sink.** In your scratch copy, change the execution call into `print`. The final
   stage is shown instead of run.
3. **Audit hook.** Python can report sensitive operations as they happen. Put this at the very top
   of a scratch file, before the code under test:

```python
import sys

def audit(event, args):
    if event.split(".")[0] in ("exec", "compile", "socket", "subprocess", "os", "urllib", "open"):
        print("AUDIT", event, repr(args)[:200], file=sys.stderr)

sys.addaudithook(audit)
```

   It logs each time the code compiles a string, opens a file, starts a process or touches the
   network. It only **logs** - it does not block anything - so it is a tool for a sandbox, not a
   safety net.
