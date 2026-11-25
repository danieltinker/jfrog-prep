# Drill answers (SPOILERS)

## Drill 01 - Plain Base64

- **Plaintext:** `FLAG{base64_ends_with_equals_and_uses_A-Za-z0-9+/}`
- **CyberChef:** From Base64
- **Python:**

```python
base64.b64decode(s)
```

## Drill 02 - Hex

- **Plaintext:** `FLAG{hex_is_only_0-9a-f_and_always_even_length}`
- **CyberChef:** From Hex
- **Python:**

```python
bytes.fromhex(s)
```

## Drill 03 - Reversed Base64

- **Plaintext:** `FLAG{if_base64_starts_with_equals_it_is_reversed}`
- **CyberChef:** Reverse (by Character) -> From Base64
- **Python:**

```python
base64.b64decode(s[::-1])
```

## Drill 04 - Base64 + zlib

- **Plaintext:** `FLAG{base64_starting_with_eJ_is_zlib_compressed_data}  FLAG{base64_starting_with_eJ_is_zlib_compressed_data}  FLAG{base64_starting_with_eJ_is_zlib_compressed_data}`
- **CyberChef:** From Base64 -> Zlib Inflate
- **Python:**

```python
zlib.decompress(base64.b64decode(s))
```

## Drill 05 - Base64 + gzip

- **Plaintext:** `FLAG{base64_starting_with_H4sI_is_gzip}  FLAG{base64_starting_with_H4sI_is_gzip}  FLAG{base64_starting_with_H4sI_is_gzip}`
- **CyberChef:** From Base64 -> Gunzip
- **Python:**

```python
gzip.decompress(base64.b64decode(s))
```

## Drill 06 - chr() list

- **Plaintext:** `FLAG{chr_lists_are_just_ascii_codes}`
- **CyberChef:** From Decimal (delimiter: Comma)
- **Python:**

```python
bytes(lst).decode()   # or ''.join(map(chr, lst))
```

## Drill 07 - ROT13

- **Plaintext:** `FLAG{rot13_keeps_punctuation_and_digits_123}`
- **CyberChef:** ROT13
- **Python:**

```python
codecs.decode(s, 'rot13')
```

## Drill 08 - Hex + XOR, key known

- **Plaintext:** `FLAG{repeating_key_xor_is_its_own_inverse}`
- **CyberChef:** From Hex -> XOR (key `jfrog`, UTF8)
- **Python:**

```python
bytes(c ^ k[i % len(k)] for i, c in enumerate(bytes.fromhex(s)))
```

## Drill 09 - Hex + XOR, single unknown byte

- **Plaintext:** `FLAG{single_byte_xor_has_only_256_keys_so_try_them_all}`
- **CyberChef:** From Hex -> XOR Brute Force (key length 1, crib `FLAG`)   [key = 0x5a]
- **Python:**

```python
raw = bytes.fromhex(s); key = raw[0] ^ ord('F'); bytes(c ^ key for c in raw)
```

## Drill 10 - PowerShell -EncodedCommand style

- **Plaintext:** `Write-Output 'FLAG{powershell_EncodedCommand_is_base64_of_UTF16LE}'`
- **CyberChef:** From Base64 -> Decode text (UTF-16LE (1200))
- **Python:**

```python
base64.b64decode(s).decode('utf-16-le')
```

## Drill 11 - Base32

- **Plaintext:** `FLAG{base32_is_uppercase_A-Z_and_2-7_only}`
- **CyberChef:** From Base32
- **Python:**

```python
base64.b32decode(s)
```

## Drill 12 - Base85 (Python b85)

- **Plaintext:** `FLAG{python_b85decode_uses_the_RFC1924_alphabet}`
- **CyberChef:** From Base85 (alphabet: IPv6)   - easier: just use Python
- **Python:**

```python
base64.b85decode(s)
```

## Drill 13 - Four fixed layers

- **Plaintext:** `FLAG{name_each_layer_before_you_remove_it}`
- **CyberChef:** From Hex -> Reverse -> From Base64 -> Zlib Inflate -> ROT13
- **Python:**

```python
codecs.decode(zlib.decompress(base64.b64decode(bytes.fromhex(s)[::-1])).decode(), 'rot13')
```

## Drill 14 - 25 identical layers

- **Plaintext:** `FLAG{twenty_five_layers_means_write_a_loop}`
- **CyberChef:** Label (`top`) -> Reverse -> From Base64 -> Zlib Inflate -> Jump (label `top`, maximum jumps 24)
- **Python:**

```python
x = s.encode()
while not x.startswith(b'FLAG'):
    x = zlib.decompress(base64.b64decode(x[::-1]))
```

## Drill 15 - RC4

- **Plaintext:** `FLAG{rc4_needs_the_key_so_find_where_the_code_builds_it}`
- **CyberChef:** From Base64 -> RC4 (passphrase `s3cr3t-k3y`, UTF8)
- **Python:**

```python
no stdlib RC4 - CyberChef, or reuse the sample's own function
```

## Drill 16 - Fernet

- **Plaintext:** `FLAG{fernet_tokens_always_start_with_gAAAAA}`
- **CyberChef:** key: SHA2 (256) -> From Hex -> To Base64 (URL safe alphabet); then Fernet Decrypt with that key
- **Python:**

```python
key = base64.urlsafe_b64encode(hashlib.sha256(b'drill-fernet').digest())
Fernet(key).decrypt(token)   # uv run --with cryptography python
```

## Drill 17 - Escapes and string building

- **Plaintext:** `FLAG{print_the_expression_never_eval_the_whole_file}`
- **CyberChef:** (left part) From Hex with `\x` delimiter / Unescape Unicode Characters
- **Python:**

```python
print(<the expression>)
```

## Drill 18 - IOC extraction

- **Plaintext:** `config: c2=https://updates.example-cdn.invalid/api/v2/checkin ; fallback=203.0.113.77:8443 ; marker=~/.cache/.lab_marker ; ua=pip/24.0 ; FLAG{write_iocs_down_defanged_hxxps_and_[.]}`
- **CyberChef:** From Hex -> XOR (key 13, HEX)
- **Python:**

```python
bytes(c ^ 0x13 for c in bytes.fromhex(s))
```
