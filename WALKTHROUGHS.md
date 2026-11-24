# Three cases, start to finish

Each case is a real, published analysis. Open the linked article in one tab and this file in
another. For every step I tell you **what you do**, **what you should notice**, and **what you say
out loud**. The decoding part of each case is matched to a drill in `drills/`, so your hands do the
same motions the researchers did.

All URLs and domains from real incidents are written defanged.

---

## Case 1 - The wheel that runs before you import it

**Article:** JFrog, "LiteLLM hijacked again" - `https://research.jfrog.com/post/litellm-hijacked-again/`
**Why this one first:** it is JFrog's own work, it is a wheel, it is pure Python, and the decoding
is Base64 + zlib. This is the closest public match to what you were told to expect.

### Step 1-2: unpack and map

- **Do:** unzip the wheel. List the files. Open `RECORD`.
- **Notice:** next to the real package folder there are files at the **top level** of the wheel
  that have nothing to do with the library: a `.pth` file, a small `.py` module with an odd name,
  and a `sitecustomize.py`.
- **Say:** "Three files do not belong. A `.pth` file is the important one: Python's `site` module
  reads every `.pth` in site-packages at startup and executes any line that begins with `import`."

How the researchers confirmed it: they compared the wheel against the sdist and the git repo. The
extra files existed **only in the wheel**. If you are given both a wheel and an sdist tomorrow,
compare their file lists - a file present in only one of them is your lead.

### Step 3: trigger

- **Do:** open the `.pth` file. It is one line: an import of the odd module.
- **Say:** "Trigger found. This runs on **every Python start** on the machine, even if the victim
  never imports the library. That is stronger than an import-time trigger."

### Step 4: sink

- **Do:** open the odd module. It is short: two imports with meaningless aliases, then one long
  line.
- **Notice:** the aliases hide the words you would search for. The import line itself still
  contains the real module names, though. Read the import line, then mentally substitute.
- **Say:** "The aliases are `zlib` and `base64`. The long line executes the result of
  zlib-decompress of Base64-decode of a literal. The literal starts with `eN` - that is the Base64
  form of the zlib header."

### Step 5: peel

- **Do:** copy only the string literal (not the quotes) into CyberChef. Recipe: **From Base64 ->
  Zlib Inflate**. Readable Python appears.
- **Your hands:** this is **Drill 04**. Do it now.
- **Say:** "One layer. Decoded statically - I did not run the sample."

### Step 6: payload

Read the article's description of the decoded stage and practise sorting it into the four
questions:

| Question | Answer in this case |
|---|---|
| Collects? | SSH keys, cloud credentials, Kubernetes config, environment variables |
| Sends? | encrypts the bundle and uploads it |
| Fetches next? | polls a public code-hosting page for further instructions (a "dead drop") |
| Stays? | the `.pth` file itself is the persistence |

Also notice the **marker**: the code sets an environment variable so it does not run twice. A
marker like that is a host IOC - mention it.

### What to take from Case 1

1. Read `RECORD` before reading code.
2. `.pth` = runs always. Know the sentence that explains why.
3. Aliased imports defeat keyword search - read the `import` lines of every small file.
4. `eJ` / `eN` at the start of Base64 means zlib.

---

## Case 2 - The line you cannot see, and the layers that never end

**Article:** Phylum (now on Veracode's blog), the W4SP stealer campaign -
`https://www.veracode.com/blog/phylum-discovers-dozens-more-pypi-packages-attempting-to-deliver-w4sp-stealer-in-ongoing-supply-chain-attack/`
**Also read:** SANS ISC diary 31634 (`https://isc.sans.edu/diary/31634`) for the many-layer peel.

### Step 1-2: unpack and map

- **Do:** unpack. The package is a **copy of a real, working library** with one change.
- **Notice:** nothing stands out in the file list. Sizes look normal. This is the hard kind.
- **Say:** "This looks like a clone of a legit package. I will check the trigger files first:
  `setup.py` if it is an sdist, then `__init__.py`."

### Step 3-4: trigger and sink

- **Do:** open the trigger file **with word wrap on**.
- **Notice:** one ordinary-looking line continues for hundreds of spaces and then has a semicolon
  and a second statement. With word wrap off, the second statement is off-screen. The statement
  does not use the plain names either: it reaches the execute and compile functions through
  `__import__` with the module name as a string.
- **Say:** "Hidden by whitespace. The sink is reached through `__import__` on the builtins
  module, so a naive search for the usual keyword at the start of a line would miss it. The
  argument is a Base64 literal."

How to catch this fast in any editor: look at the horizontal scrollbar, or search with a regex for
"30 or more spaces followed by a non-space".

### Step 5: peel, stage by stage

- **Layer 1.** Base64 -> a few lines of Python that fetch a URL and run what comes back.
  **Your hands: Drill 01.** *Say:* "Stage 0 is a downloader. The URL is an IOC. I would not fetch
  it from this machine. If you can give me the next stage, I will continue."
- **Next stage.** In the W4SP case the fetched code is the "tiny lambda that decompresses, then a
  huge literal" shape, wrapped around itself many times. Each time you decode, you get the same
  shape again with a smaller literal.
- **Notice the repetition after the second round and stop doing it by hand.**
  **Your hands: Drill 14.** Write the loop. It is six lines.
- **Say:** "The same wrapper repeats. I will loop: reverse if needed, Base64-decode,
  zlib-decompress, and stop when the output no longer looks like a wrapped literal."

### Step 6: payload

A stealer. Practise the ten-second recognition from the playbook table: browser profile paths,
the chat-app token locations, wallet names, then an upload to a webhook.

### What to take from Case 2

1. Word wrap is not optional.
2. A downloader stage means the sample in your hands may not contain the final payload. Say so,
   name the URL as an IOC, ask for the next stage.
3. Second time you see the same shape -> loop.

---

## Case 3 - Encrypted, keyed, and reluctant to run

**Articles:**
- Mend, the Fernet campaign - `https://www.mend.io/blog/over-100-malicious-packages-target-popular-ml-pypi-libraries/`
- JFrog, "Revival Hijack" (environment-gated loader) - `https://jfrog.com/blog/revival-hijack-pypi-hijack-technique-exploited-22k-packages-at-risk/`
- Phylum on beating an obfuscator by printing - `https://www.veracode.com/blog/malicious-open-source-package-authors-are-bad-and-should-feel-bad/`

This case combines three things that stop beginners: real encryption, ugly names, and a guard.

### The encryption

- **Notice:** a long token starting with `gAAAAA` and, close by, a 44-character Base64 string
  ending in `=`. The code imports `Fernet`.
- **Say:** "`gAAAAA` is the fixed start of a Fernet token. Fernet is symmetric, so the key must be
  in the package. That 44-character string is the key."
- **Do:** CyberChef **Fernet Decrypt**, paste key and token. Or three lines of Python.
- **Your hands: Drill 16.**
- **The principle:** symmetric encryption in a self-contained sample is just another encoding.
  The key is always there. Your job is to find where the code builds it - it may be split into
  pieces, reversed, or computed.

### The ugly names

- **Notice:** every identifier is some mix of `O`, `0`, `l`, `I`. There is a function of 15 lines
  doing arithmetic on byte lists. There are lists of strings; some are never used.
- **Do not** try to understand the arithmetic. Do this:
  1. Find the sink. Walk backwards: which variable goes into it? Which function produced that
     variable? What are that function's inputs?
  2. Rename those three or four things with find-and-replace: `decrypt`, `key`, `data`.
  3. Copy the function, the key lines and the data lines into your own `scratch.py`.
  4. Replace the sink with `print`.
  5. Read your scratch file once to confirm it is only arithmetic. Run it.
- **Say:** "I do not need to identify the cipher. The sample contains its own decryptor, so I let
  it decrypt its own data and print the result instead of executing it."
- **Your hands: Drill 15** (RC4 with a given key, in CyberChef) shows the other route: if you
  *do* recognise the cipher and have the key, CyberChef does it without running anything.

Bonus point if you recognise it: a 256-element list being shuffled and then used to XOR a stream
is RC4. Say "this looks like RC4" and move on.

### The guard

- **Notice:** you run your scratch copy and nothing happens. Or the decoded stage begins with
  conditions: is this Windows, is a certain environment variable present, is the user name on a
  list, is a debugger attached.
- **Say:** "This is an environment check. The Revival Hijack sample only ran when a CI server's
  environment variable existed - it was aimed at build machines. A guard tells us who the target
  is, which is worth a line in the report."
- **Do:** do not try to satisfy the guard. Copy the decoding lines out from under it into
  `scratch.py`.

### The key that changes

One more trap from the same family: the key is derived from `__name__`, `__file__`, or the
package's own name. In your scratch file those values are different, so decryption gives garbage.

- **Say:** "The key depends on runtime context. On a victim, this module is imported as
  `package.module`, so `__name__` has that value. I will hard-code the victim's value."

### What to take from Case 3

1. `gAAAAA` = Fernet. The key is in the package.
2. Unreadable code: sink -> walk back -> copy their decoder -> print.
3. Nothing happens = a guard. Lift the decoder out.
4. Garbage with the right method = wrong key context.

---

## A final stage inside a final stage

Twice in these cases the "payload" contained one more encoded string: a Base64 argument handed to
PowerShell. It decodes to text with a NUL byte between every character.

- **Say:** "PowerShell's encoded-command parameter is Base64 of UTF-16LE."
- **Do:** From Base64 -> Decode text (UTF-16LE).
- **Your hands: Drill 10.**

---

## Self-test (cover the answers)

1. You get a `.whl`. First three actions? -> *hash it, unzip it, read `RECORD`.*
2. Wheel, clean `__init__.py`, but there is `foo.pth`. What do you say? -> *runs on every Python start; open it, follow the import.*
3. Base64 that starts with `==`? -> *reversed.*
4. Base64 that starts with `eJ`? `H4sI`? `gAAAAA`? -> *zlib, gzip, Fernet.*
5. Decoded bytes show `h.t.t.p.` with dots between letters? -> *UTF-16LE.*
6. No `exec` or `eval` in any file. Next search? -> *`getattr`, `__import__`, `builtins`, `compile`, `subprocess`; then `.pth` and data files.*
7. The decoder is 40 lines of `O0O0`. What do you do? -> *copy it to scratch, print instead of execute.*
8. Your scratch copy gives garbage but the method is right. Why? -> *key depends on `__name__` / `__file__` / host.*
9. You decode stage 0 and it only downloads a URL. What now? -> *URL is an IOC, do not fetch, report it, ask for the next stage.*
10. "Is obfuscation proof of malware?" -> *no: a signal, not a verdict; judge behaviour.*
