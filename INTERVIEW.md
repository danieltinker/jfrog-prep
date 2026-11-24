# The interview: what to expect and how to behave

## What is actually known

I searched Glassdoor, TheWorker, Reddit, Blind, LinkedIn and Hebrew sources. **No public first-hand
account of this specific interview exists.** So the format below comes from three things: what you
were told, the job post, and how the JFrog research team writes about its own work.

**You were told:** hands-on, no AI, a malicious PyPI package (wheel file, pure Python, nothing
compiled), find the payload by hand. CyberChef, running code, logging/prints are allowed. CTF style.

**The job post** (join.jfrog.com, "Malware Researcher", Netanya/Tel Aviv) asks for someone who will:

- research malicious code in public repositories across languages,
- define and implement ways to **automatically detect** malicious code,
- **write technical reports** and public publications,
- program in Python.

So the exercise tests three things, in this order: can you *find* it, can you *decode* it, can you
*explain* it clearly. The third one is where candidates lose points without noticing.

**Ask in the first minute of the interview.** There is nobody to ask beforehand, and asking is
normal - it shows you check the rules before you touch a sample:

1. Is Google / the official Python docs allowed, or only no-AI?
2. May I use my own notes?
3. Am I allowed to run code from the sample, or static only?
4. Is this machine isolated, or should I treat it as a real workstation?

**Because you do not know the machine, be ready for both.** Assume Linux or macOS with a terminal.
If it is your own laptop: CyberChef downloaded for offline use, AI extensions off. If it is
theirs: you may have only Python and a browser, so know the pure-Python ways to unpack
(`python -m zipfile -e`, `python -m tarfile -e`) and to decode (the REPL snippets in the cheatsheet).

## The team's vocabulary - use these words out loud

| Word | Meaning |
|---|---|
| **Infection vector** | How the package reaches victims: typosquatting, dependency confusion, a hijacked legit package, a "trojan" package with real features |
| **Trigger** | When the code runs: at install (sdist `setup.py`), at import (`__init__.py`), at every interpreter start (`.pth`, `sitecustomize.py`), or when a function is called |
| **Stage / loader / dropper** | Stage 0 is the small visible piece. It decodes or downloads stage 1, and so on |
| **Payload** | The final thing that does the damage |
| **Stealer / infostealer** | Collects tokens, cookies, wallets, SSH keys, env vars |
| **Exfiltration** | How the data leaves: webhook, bot API, plain HTTP POST, DNS |
| **C2** | The server the malware talks to. A "dead drop" is a public page (paste, gist) holding the next instruction |
| **Persistence** | How it survives a reboot: startup folder, scheduled task, cron, `.pth` |
| **IOC** | Indicator of compromise: URL, domain, IP, file path, file hash, env-var marker |

Their own position on obfuscation, from a 2026 JFrog post: obfuscation is **"a signal, not a
verdict"**. Legit packages obfuscate to protect IP. You judge by behaviour. Say this if asked.

## How to behave during the exercise

**Talk the whole time.** They cannot grade thoughts they cannot hear. A wrong hypothesis said out
loud and then corrected looks good. Silence followed by a right answer looks like luck.

Use this sentence pattern over and over:

> "I see **X**. That suggests **Y**. I will check it by doing **Z**."

Example: "I see a 4,000-character string starting with `eJ`. That suggests Base64 over zlib. I will
decode it in CyberChef and check that the first bytes are `78 9c`."

**Keep notes as you go** in a text file, visible on screen. Three headings: *Trigger*, *Layers*,
*IOCs*. Each time you remove a layer, write one line. When they ask "so what does it do?" you read
your notes instead of scrolling around in panic.

**State your safety stance in the first minute:**

> "I will not `pip install` this. I will unpack it as an archive and read it. I decode statically
> first. If I run anything, I run only the decoding part, with the execution call replaced by a
> print."

This is exactly how JFrog describes its own work ("static decoding, without executing the sample").
Saying it early shows you already work the way they do.

**When you are stuck for more than 3 minutes, say so and name your next two options.** "This layer
does not decode as Base64. Either the alphabet is different or there is a step before it. I will
look at how the code itself decodes it." Interviewers give hints to people who think out loud.

**Stop when you reach the payload.** Do not keep decoding forever. Say: "This is the final stage.
It does A, B, C. Here are the IOCs."

## The 2-minute verbal report to give at the end

Follow the skeleton JFrog uses in its own posts. Fill in one line each:

1. **Summary** - "Package `<name>` pretends to be `<legit thing>`. It is a `<stealer / downloader / ...>`."
2. **Trigger** - "The code runs at `<install / import / interpreter start>`, from `<file>:<line>`."
3. **Obfuscation** - "`<N>` layers: `<hex, reversed, Base64, zlib, XOR with key K ...>`. The key came from `<where>`."
4. **Behaviour** - "The final stage `<collects X>`, sends it to `<Y>`, and `<persists / downloads Z>`."
5. **Guards** - "It only runs when `<Windows / not in CI / env var set ...>`."
6. **IOCs** - URLs, domains, paths, markers. Written defanged: `hxxps://evil[.]example/api`.
7. **Detection idea** - one rule, plus its false-positive risk (see below).
8. **Confidence and gaps** - "I did not fetch the second stage, so its behaviour is inferred."

## Follow-up questions you should expect

These are inferred from the job post ("automatically detect") and JFrog's Xray documentation, not
from candidate reports.

**"How would you detect this automatically?"**
Give a layered answer. (1) Static signals: dynamic execution of decoded data, very long string
literals, very long lines, code that runs at install or in a `.pth`, network + process APIs in a
package whose purpose does not need them. (2) Metadata signals: name close to a popular package,
brand-new account, version jump, wheel contains files the sdist or the git repo does not. (3)
Scoring: each signal adds to a score, high scores are blocked automatically, middle scores go to a
human. JFrog Xray documents exactly this "maliciousness score" model.

**"What false positives would that give?"**
Always have one ready. Base64 + exec also appears in legit packers and in some test suites. Long
strings appear in embedded certificates, fonts and test fixtures. Install-time code is normal for
packages that compile C. So no single signal is enough - combine them.

**"When does `setup.py` run? Can a wheel run code at install?"**
`setup.py` exists only in a source distribution (sdist, `.tar.gz`). Installing from an sdist builds
it on your machine, which runs `setup.py`. A wheel is a pre-built zip. Installing it only copies
files, no package code runs. So wheel malware needs another trigger: import time, a `.pth` file
(runs at every Python start, even if you never import the package), or an entry-point script.

**"Is obfuscated code always malicious?"**
No. Signal, not verdict. Decide by what the decoded code does.

**"How would you find other packages from the same actor?"**
Pivot on the IOCs: same C2 domain or webhook, same obfuscator output shape, same author e-mail or
account, same odd marker string or variable name, same upload time window.

**"How would you analyse this safely for real?"**
Disposable VM or container, no credentials inside, no host mounts, network off or sinkholed.
Static first. Never `pip install` or `pip download` an sdist - both can run its build code.

**"What would you tell an affected user?"**
Uninstall is not enough. Rotate every secret the machine had (env vars, SSH keys, cloud and CI
tokens), look for the persistence artefacts, check for the IOCs in logs.

## Day-of checklist

- [ ] CyberChef open in a tab (and downloaded for offline use: the page has a "Download CyberChef" link).
- [ ] Editor with **word wrap ON** and "render whitespace" ON. Copilot and every AI extension **disabled**.
- [ ] A scratch folder, an empty `notes.txt`, a Python REPL ready.
- [ ] Reread `CHEATSHEET.md` once, 30 minutes before. Do not learn anything new in the last hour.
- [ ] Water. Slow down. Read the file list before you read any code.
