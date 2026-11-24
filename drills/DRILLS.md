# Decode drills

Goal: recognise an encoding **by its look** and remove it in under a minute.
Do each one twice: once in CyberChef, once in a Python REPL. All plaintexts are harmless.
Answers: `solutions/drills.md` - look only after you tried for 5 minutes.

## Drill 01

A string.

Full text, one line: `drills/d01.txt`

```
RkxBR3tiYXNlNjRfZW5kc193aXRoX2VxdWFsc19hbmRfdXNlc19BLVphLXowLTkrL30=
```

## Drill 02

A string.

Full text, one line: `drills/d02.txt`

```
464c41477b6865785f69735f6f6e6c795f302d39612d665f616e645f616c776179735f6576656e5f6c656e6774687d
```

## Drill 03

A string. Look at where the `=` padding is.

Full text, one line: `drills/d03.txt`

```
==QfkV2cyVmdlJ3Xzl2X0l2XzxWY1FXZfhGdpd3XzRnchR3cfRjNlNXYi9lZpt3RBxkR
```

## Drill 04

A string. Decode it once and look at the first bytes (hex `78 9c`).

Full text, one line: `drills/d04.txt`

```
eJxz83F0r05KLE41M4kvLkksKsnMS48vzyzJiE/1is8sjq/KyUyKT87PLShKLS5OTYlPSSxJrFVQcKOrNgCBfz9q
```

## Drill 05

A string.

Full text, one line: `drills/d05.txt`

```
H4sIAAAAAAACE3PzcXSvTkosTjUziS8uSSwqycxLjy/PLMmI9zAp9ozPLI5Pr8osqFVQcKO6QgB0mXL2ewAAAA==
```

## Drill 06

A Python list of integers.

Full text, one line: `drills/d06.txt`

```
[70, 76, 65, 71, 123, 99, 104, 114, 95, 108, 105, 115, 116, 115, 95, 97, 114, 101, 95, 106, 117, 115, 116, 95, 97, 115, 99, 105, 105, 95, 99, 111, 100...   (166 chars)
```

## Drill 07

A string. The braces and underscores survived - only letters moved.

Full text, one line: `drills/d07.txt`

```
SYNT{ebg13_xrrcf_chapghngvba_naq_qvtvgf_123}
```

## Drill 08

Hex string. The key is the ASCII text `jfrog`.

Full text, one line: `drills/d08.txt`

```
2c2a33281c1803020a061e0f1c083801030b301f05142d0614350f061c3805111c300e0410171d140f1b
```

## Drill 09

Hex string, XORed with ONE unknown byte. The plaintext starts with `FLAG{`.

Full text, one line: `drills/d09.txt`

```
1c161b1d212933343d363f0538232e3f0522352805323b29053534362305686f6c05313f2329052935052e2823052e323f37053b363627
```

## Drill 10

A Base64 string. After decoding you will see a NUL byte between every letter.

Full text, one line: `drills/d10.txt`

```
VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAEYATABBAEcAewBwAG8AdwBlAHIAcwBoAGUAbABsAF8ARQBuAGMAbwBkAGUAZABDAG8AbQBtAGEAbgBkAF8AaQBzAF8AYgBhAHMAZQA2ADQAXwBvAG...   (180 chars)
```

## Drill 11

A string. Only capitals and the digits 2-7.

Full text, one line: `drills/d11.txt`

```
IZGECR33MJQXGZJTGJPWS427OVYHAZLSMNQXGZK7IEWVUX3BNZSF6MRNG5PW63TMPF6Q====
```

## Drill 12

A string full of punctuation, produced by Python `base64.b85encode`.

Full text, one line: `drills/d12.txt`

```
Mod9RdvJMlXm4&`VmLKqWn*t-WnXo3WpiJ2Xk}kgMnf?<GBjUdY;b5{Vr6uF
```

## Drill 13

A string. Work out each layer from what the data LOOKS like, one at a time.

Full text, one line: `drills/d13.txt`

```
3d6b5645622b474146383653766f494c4b726b71743845694b6e307a4b3269534f70794c50336f5370734d7a7632494b726f384c4b7179714d3755714c51766a4c774a65
```

## Drill 14

Each layer is: reverse -> Base64 -> zlib. There are many layers. Do NOT do this by hand.

Full text, one line: `drills/d14.txt`

```
==gLRW3yfo+ncGeI/FoYkI5WkMV8ylsrYhUxZKjXN5GqCtkmxSe7vbcoYN4CRUGAKkN9b+DRIQc0kykjmjYoGc627+7A5b2V60+B/OeW2Bf4LM42UxsH5T4dZ1fiUFx4J2NdJQPrr+rPLQ0PrEVc3b...   (1248 chars)
```

## Drill 15

Base64 string. RC4-encrypted with the ASCII key `s3cr3t-k3y`.

Full text, one line: `drills/d15.txt`

```
pOhH7CKbZuJea8HbfL9mSVp0ms8gbj0AvJSutxbScREOYrGO6/cEWZ56vacw2kAR26n4SckvK7k=
```

## Drill 16

A token. The key is not written down - the code would BUILD it: URL-safe Base64 of the SHA-256 digest of the ASCII text `drill-fernet`. Build the key first, then decrypt.

Full text, one line: `drills/d16.txt`

```
gAAAAABrBcDJbetR62uoA_RL_fTrxvlSSL-QbpBQTfmfqmH_r6_BjOOL4RGMKHMQ2RsvD47xX9YuDnuPq_Y4VX2lAf8Y5z_wzKAa3ftIrXiN5MSxOvyvhGHhhWINp53hQNDNsGz43sBN
```

## Drill 17

A Python EXPRESSION made only of string literals. Paste it into `print(...)` in a REPL.

Full text, one line: `drills/d17.txt`

```
"\x46\x4c\x41\x47\x7b\x70\x72\x69\x6e\x74\x5f\x74\x68\x65\x5f\x65\x78" + "\u0070\u0072\u0065\u0073\u0073\u0069\u006f\u006e\u005f\u006e\u0065\u0076\u00...   (242 chars)
```

## Drill 18

Hex of XOR(0x13) data. Decode it, then list every indicator you would put in a report (defanged).

Full text, one line: `drills/d18.txt`

```
707c7d757a74293370212e7b67676360293c3c666377726776603d766b727e637f763e70777d3d7a7d65727f7a773c72637a3c65213c707b7670787a7d33283375727f7f717270782e2123...   (362 chars)
```
