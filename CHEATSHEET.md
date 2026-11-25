# Cheatsheet (read this one 30 minutes before)

## The method in one line

**Unpack -> Map -> Trigger -> Sink -> Peel -> Payload -> Report.** Never install. Find the sink,
walk backwards. One layer at a time, name it, write it down.

## Unpack

```bash
shasum -a 256 sample.whl          # record the hash
unzip sample.whl -d out/          # a wheel is a zip
tar xzf sample.tar.gz -C out/     # an sdist is a tarball
find out -type f | xargs ls -la   # every file with its size
cat out/*.dist-info/RECORD        # the full list of installed files
cat out/*.dist-info/METADATA      # name, author, homepage, Requires-Dist
```

Windows without `unzip`: rename `.whl` to `.zip`, or `python -m zipfile -e sample.whl out/`.
`python -m tarfile -e sample.tar.gz out/` works for sdists.

## Where code can start

| Place | Runs when |
|---|---|
| `setup.py` (sdist only): top-level code, `cmdclass=` | install |
| `*.pth` line starting with `import` | every Python start |
| `sitecustomize.py` | every Python start |
| `__init__.py` and everything it imports | `import pkg` |
| `entry_points.txt` | user runs the command |

A wheel has **no `setup.py`**. Installing a wheel only copies files.

## Words to search

`exec` `eval` `compile` `marshal` `pickle` `__import__` `getattr` `builtins` `globals` `importlib`
`subprocess` `os.system` `Popen` `powershell` `b64decode` `fromhex` `unhexlify` `decompress`
`codecs` `Fernet` `chr(` `[::-1]` `urllib` `requests` `socket` `http` `webhook` `os.environ`

Then: **word wrap ON**, find the **longest line**, sort files **by size**.

## Recognise an encoding by its look

| It looks like | It is | Remove with |
|---|---|---|
| `A-Z a-z 0-9 + /`, ends with `=` or `==` | Base64 | From Base64 |
| same but with `-` and `_` | URL-safe Base64 | From Base64 (URL safe alphabet) |
| *starts* with `=` | reversed Base64 | Reverse, then From Base64 |
| only `0-9 a-f`, even length | hex | From Hex |
| `\x41\x42` or `A` | escaped string | just `print("...")` it |
| `[104, 116, 116, 112]` | list of character codes | From Decimal / `bytes(list)` |
| only `A-Z` and `2-7`, `=` padding | Base32 | From Base32 |
| lots of punctuation `!#$%&()*+` | Base85 | `base64.b85decode` or `a85decode` |
| readable shape, wrong letters, `{}` and `_` intact | ROT13 / Caesar | ROT13 |
| `uggcf://` | ROT13 of `https://` | ROT13 |
| every other character is `A`: `SQBFAFgA...` | Base64 of UTF-16LE (PowerShell) | From Base64, Decode text UTF-16LE |
| random bytes, a key nearby | XOR / RC4 / AES | find the key in the code |

## Recognise what is *inside* by its first characters

| Base64 starts with | Raw hex starts with | Content |
|---|---|---|
| `eJ` (also `eN`, `eA`) | `78 9c` (`78 da`, `78 01`) | zlib -> Zlib Inflate |
| `H4sI` | `1f 8b` | gzip -> Gunzip |
| `gAAAAA` | - | Fernet token -> Fernet Decrypt, needs the key |
| `aW1wb3J0` | | the text `import` - you reached Python source |
| `ZXhlYy` | | the text `exec` |
| `ZnJvbS` / `ZGVmI` | | the text `from ` / `def ` |
| `aHR0c` | | the text `http` |
| `eyJ` | `7b 22` | JSON `{"` |
| `UEsDB` | `50 4b 03 04` | zip archive |
| `TVqQ` / `TVo` | `4d 5a` | Windows executable (MZ) |
| `f0VMR` | `7f 45 4c 46` | Linux executable (ELF) |
| `iVBORw0KGgo` | `89 50 4e 47` | PNG image |
| `gASV` | `80 04 95` | Python pickle |
| `4w` or `Yw` | `e3` or `63` | Python marshal code object |

Check the first bytes after every decode: CyberChef **To Hex**, or `print(data[:8].hex())`.

## Python REPL snippets (type these from memory)

```python
import base64, zlib, gzip, codecs, binascii

s = open("blob.txt").read().strip()          # the blob, saved to a file, one line

base64.b64decode(s)                          # Base64
base64.b64decode(s + "=" * (-len(s) % 4))    # Base64 with missing padding
base64.urlsafe_b64decode(s)                  # - and _ alphabet
base64.b64decode(s[::-1])                    # reversed first
base64.b32decode(s); base64.b85decode(s); base64.a85decode(s)
bytes.fromhex(s)                             # hex
zlib.decompress(data); gzip.decompress(data) # compression
codecs.decode(text, "rot13")                 # rot13
bytes([104, 116, 116, 112]).decode()         # list of codes -> text
data.decode("utf-16-le")                     # PowerShell encoded command

# XOR with a repeating key
key = b"secret"
bytes(c ^ key[i % len(key)] for i, c in enumerate(data))

# XOR with one unknown byte, known first letter of the plaintext
key = data[0] ^ ord("i")                     # guess: starts with "import"
bytes(c ^ key for c in data)

# XOR with one unknown byte, no idea of the plaintext: try all 256
for k in range(256):
    out = bytes(c ^ k for c in data)
    if b"http" in out or b"import" in out:
        print(k, out[:80])

# many identical layers: loop until it stops looking like a blob
x = s.encode()
while not x.lstrip().startswith((b"import", b"from", b"def", b"#", b"FLAG")):
    x = zlib.decompress(base64.b64decode(x[::-1]))
print(x.decode())

# always look before you trust
print(type(x), len(x), repr(x[:200]))
```

Fernet needs a library: `uv run --with cryptography python`, then
`from cryptography.fernet import Fernet; Fernet(key).decrypt(token)`. Or CyberChef "Fernet Decrypt".

## Read an expression inside-out

```
sink( zlib.decompress( base64.b64decode( blob[::-1] ) ) )
                                          3. reverse      <- happens FIRST
                        2. Base64 decode
      1. zlib inflate                                      <- happens LAST
```

CyberChef recipe = innermost first: **Reverse -> From Base64 -> Zlib Inflate**.

## CyberChef operations worth knowing by name

From Base64 · From Hex · From Decimal · From Base32 · From Base85 · Reverse · ROT13 · XOR ·
XOR Brute Force · Zlib Inflate · Gunzip · Raw Inflate · Decode text · Fernet Decrypt · RC4 ·
AES Decrypt · Unescape string · Magic · To Hex · Extract URLs · Defang URL · Regular expression

- **Magic** is a first hint, not the method. Tested: it solves Base64 -> zlib, but it stops at
  reversed data (it found From Hex on Drill 13 and nothing after).
- **XOR** with a text key: change the key dropdown from **HEX** to **UTF8**, or the key is misread.
- Many identical layers, no Python: **Label** (name `top`) -> the layer's operations -> **Jump**
  (label `top`, maximum jumps = layers - 1). Too few jumps: output still looks encoded. Too many:
  an error such as "Zlib Inflate - unsupported compression method". Raise the number until readable.
- **Extract URLs** then **Defang URL** gives you the IOC list for the report in two clicks.
- **To Hex** on the output shows the magic bytes of the next layer.
- The pause/breakpoint icon on an operation lets you look at one layer at a time.

## Stuck? (full version in PLAYBOOK.md)

| Symptom | First thing to try |
|---|---|
| no `exec` anywhere | search `getattr`, `__import__`, `builtins`, then `.pth` and non-`.py` files |
| cannot find the start | reread `RECORD`; open every imported module |
| decode is garbage | reread the expression inside-out; reverse? padding? alphabet? |
| still garbage after decode | look at first bytes: compressed? encrypted (find key)? |
| key gives garbage | key depends on `__name__` / `__file__` / hostname - use the victim's value |
| ran it, nothing printed | a guard (OS, user, env, date) or a swallowed exception |
| code is unreadable | find the sink, walk backwards, copy their decoder to `scratch.py`, print |

## The answer they want at the end

**Trigger** (file:line, when) · **Layers** (in order, with keys) · **Behaviour** (collects, sends,
fetches, persists) · **Guards** · **IOCs, defanged** · **One detection idea + its false positive**.
