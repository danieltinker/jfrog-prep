"""SPOILERS. Generates drills/DRILLS.md and solutions/drills.md.

Data-only encoding practice: every plaintext is a harmless sentence. Nothing here
executes anything. Run:  uv run --no-project --with cryptography python solutions/make_drills.py
"""
import base64, codecs, gzip, hashlib, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
b64 = lambda b: base64.b64encode(b).decode()


def xor(data, key):
    return bytes(c ^ key[i % len(key)] for i, c in enumerate(data))


def rc4(key, data):
    s, j, out = list(range(256)), 0, bytearray()
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    for c in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(c ^ s[(s[i] + s[j]) % 256])
    return bytes(out)


def lines(s, w=76):
    return "\n".join(s[i:i + w] for i in range(0, len(s), w))


D = []  # (title, what you are given, blob, plaintext, cyberchef recipe, python)


def add(title, given, blob, plain, chef, py):
    D.append((title, given, blob, plain, chef, py))


p = "FLAG{base64_ends_with_equals_and_uses_A-Za-z0-9+/}"
add("Plain Base64", "A string.", b64(p.encode()), p, "From Base64", "base64.b64decode(s)")

p = "FLAG{hex_is_only_0-9a-f_and_always_even_length}"
add("Hex", "A string.", p.encode().hex(), p, "From Hex", "bytes.fromhex(s)")

p = "FLAG{if_base64_starts_with_equals_it_is_reversed}"
add("Reversed Base64", "A string. Look at where the `=` padding is.", b64(p.encode())[::-1], p,
    "Reverse (by Character) -> From Base64", "base64.b64decode(s[::-1])")

p = "FLAG{base64_starting_with_eJ_is_zlib_compressed_data}  " * 3
add("Base64 + zlib", "A string. Decode it once and look at the first bytes (hex `78 9c`).",
    b64(zlib.compress(p.encode())), p.strip(), "From Base64 -> Zlib Inflate", "zlib.decompress(base64.b64decode(s))")

p = "FLAG{base64_starting_with_H4sI_is_gzip}  " * 3
add("Base64 + gzip", "A string.", b64(gzip.compress(p.encode(), mtime=0)), p.strip(),
    "From Base64 -> Gunzip", "gzip.decompress(base64.b64decode(s))")

p = "FLAG{chr_lists_are_just_ascii_codes}"
add("chr() list", "A Python list of integers.", str([ord(c) for c in p]), p,
    "From Decimal (delimiter: Comma)", "bytes(lst).decode()   # or ''.join(map(chr, lst))")

p = "FLAG{rot13_keeps_punctuation_and_digits_123}"
add("ROT13", "A string. The braces and underscores survived - only letters moved.", codecs.encode(p, "rot13"), p,
    "ROT13", "codecs.decode(s, 'rot13')")

p = "FLAG{repeating_key_xor_is_its_own_inverse}"
add("Hex + XOR, key known", "Hex string. The key is the ASCII text `jfrog`.", xor(p.encode(), b"jfrog").hex(), p,
    "From Hex -> XOR (key `jfrog`, UTF8)", "bytes(c ^ k[i % len(k)] for i, c in enumerate(bytes.fromhex(s)))")

p = "FLAG{single_byte_xor_has_only_256_keys_so_try_them_all}"
add("Hex + XOR, single unknown byte", "Hex string, XORed with ONE unknown byte. The plaintext starts with `FLAG{`.",
    xor(p.encode(), b"\x5a").hex(), p,
    "From Hex -> XOR Brute Force (key length 1, crib `FLAG`)   [key = 0x5a]",
    "raw = bytes.fromhex(s); key = raw[0] ^ ord('F'); bytes(c ^ key for c in raw)")

p = "Write-Output 'FLAG{powershell_EncodedCommand_is_base64_of_UTF16LE}'"
add("PowerShell -EncodedCommand style", "A Base64 string. After decoding you will see a NUL byte between every letter.",
    b64(p.encode("utf-16-le")), p, "From Base64 -> Decode text (UTF-16LE (1200))",
    "base64.b64decode(s).decode('utf-16-le')")

p = "FLAG{base32_is_uppercase_A-Z_and_2-7_only}"
add("Base32", "A string. Only capitals and the digits 2-7.", base64.b32encode(p.encode()).decode(), p,
    "From Base32", "base64.b32decode(s)")

p = "FLAG{python_b85decode_uses_the_RFC1924_alphabet}"
add("Base85 (Python b85)", "A string full of punctuation, produced by Python `base64.b85encode`.",
    base64.b85encode(p.encode()).decode(), p,
    "From Base85 (alphabet: IPv6)   - easier: just use Python", "base64.b85decode(s)")

p = "FLAG{name_each_layer_before_you_remove_it}"
blob = b64(zlib.compress(codecs.encode(p, "rot13").encode()))[::-1].encode().hex()
add("Four fixed layers", "A string. Work out each layer from what the data LOOKS like, one at a time.", blob, p,
    "From Hex -> Reverse -> From Base64 -> Zlib Inflate -> ROT13",
    "codecs.decode(zlib.decompress(base64.b64decode(bytes.fromhex(s)[::-1])).decode(), 'rot13')")

p = "FLAG{twenty_five_layers_means_write_a_loop}"
x = p.encode()
for _ in range(25):
    x = base64.b64encode(zlib.compress(x))[::-1]
add("25 identical layers", "Each layer is: reverse -> Base64 -> zlib. There are many layers. Do NOT do this by hand.",
    x.decode(), p, "Label (`top`) -> Reverse -> From Base64 -> Zlib Inflate -> Jump (label `top`, maximum jumps 24)",
    "x = s.encode()\nwhile not x.startswith(b'FLAG'):\n    x = zlib.decompress(base64.b64decode(x[::-1]))")

p = "FLAG{rc4_needs_the_key_so_find_where_the_code_builds_it}"
add("RC4", "Base64 string. RC4-encrypted with the ASCII key `s3cr3t-k3y`.", b64(rc4(b"s3cr3t-k3y", p.encode())), p,
    "From Base64 -> RC4 (passphrase `s3cr3t-k3y`, UTF8)", "no stdlib RC4 - CyberChef, or reuse the sample's own function")

p = "FLAG{fernet_tokens_always_start_with_gAAAAA}"
try:
    from cryptography.fernet import Fernet
    fkey = base64.urlsafe_b64encode(hashlib.sha256(b"drill-fernet").digest())
    add("Fernet", "A token. The key is not written down - the code would BUILD it: URL-safe Base64 of the "
        "SHA-256 digest of the ASCII text `drill-fernet`. Build the key first, then decrypt.",
        Fernet(fkey).encrypt(p.encode()).decode(), p,
        "key: SHA2 (256) -> From Hex -> To Base64 (URL safe alphabet); then Fernet Decrypt with that key",
        "key = base64.urlsafe_b64encode(hashlib.sha256(b'drill-fernet').digest())\n"
        "Fernet(key).decrypt(token)   # uv run --with cryptography python")
except ImportError:
    pass

p = "FLAG{print_the_expression_never_eval_the_whole_file}"
h = len(p) // 3
expr = ('"' + "".join(f"\\x{ord(c):02x}" for c in p[:h]) + '" + "' + "".join(f"\\u{ord(c):04x}" for c in p[h:2 * h])
        + '" + bytes.fromhex("' + p[2 * h:].encode().hex() + '").decode()')
add("Escapes and string building", "A Python EXPRESSION made only of string literals. Paste it into `print(...)` in a REPL.",
    expr, p, "(left part) From Hex with `\\x` delimiter / Unescape Unicode Characters", "print(<the expression>)")

p = ("config: c2=https://updates.example-cdn.invalid/api/v2/checkin ; "
     "fallback=203.0.113.77:8443 ; marker=~/.cache/.lab_marker ; ua=pip/24.0 ; "
     "FLAG{write_iocs_down_defanged_hxxps_and_[.]}")
add("IOC extraction", "Hex of XOR(0x13) data. Decode it, then list every indicator you would put in a report (defanged).",
    xor(p.encode(), b"\x13").hex(), p, "From Hex -> XOR (key 13, HEX)",
    "bytes(c ^ 0x13 for c in bytes.fromhex(s))")

drills, sols = ["# Decode drills\n",
                "Goal: recognise an encoding **by its look** and remove it in under a minute.\n"
                "Do each one twice: once in CyberChef, once in a Python REPL. All plaintexts are harmless.\n"
                "Answers: `solutions/drills.md` - look only after you tried for 5 minutes.\n"], ["# Drill answers (SPOILERS)\n"]
for n, (title, given, blob, plain, chef, py) in enumerate(D, 1):
    (ROOT / "drills").mkdir(exist_ok=True)
    (ROOT / f"drills/d{n:02d}.txt").write_text(blob + "\n")
    shown = blob if len(blob) <= 160 else blob[:150] + f"...   ({len(blob)} chars)"
    drills.append(f"## Drill {n:02d}\n\n{given}\n\nFull text, one line: `drills/d{n:02d}.txt`\n\n```\n{shown}\n```\n")
    sols.append(f"## Drill {n:02d} - {title}\n\n- **Plaintext:** `{plain}`\n- **CyberChef:** {chef}\n- **Python:**\n\n```python\n{py}\n```\n")
(ROOT / "drills").mkdir(exist_ok=True)
(ROOT / "drills/DRILLS.md").write_text("\n".join(drills))
(ROOT / "solutions/drills.md").write_text("\n".join(sols))

# self-check: the documented Python really decodes the blob
assert base64.b64decode(D[2][2][::-1]).decode() == D[2][3]
assert codecs.decode(zlib.decompress(base64.b64decode(bytes.fromhex(D[12][2])[::-1])).decode(), "rot13") == D[12][3]
x = D[13][2].encode()
while not x.startswith(b"FLAG"):
    x = zlib.decompress(base64.b64decode(x[::-1]))
assert x.decode() == D[13][3]
assert rc4(b"s3cr3t-k3y", base64.b64decode(D[14][2])).decode() == D[14][3]
assert eval(D[16][2]) == D[16][3]  # our own literal-only expression
print(f"wrote {len(D)} drills")
