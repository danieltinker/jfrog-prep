# JFrog Malware Researcher - hands-on interview prep

Task tomorrow: you get a malicious PyPI package (a wheel, pure Python). You find the payload by
hand. No AI. CyberChef, a Python REPL, running and logging code are allowed.

## What is in this folder

| File | What it is | When |
|---|---|---|
| `PLAYBOOK.md` | The 7-step method, plus what to do for every way of getting stuck | Read first, tonight |
| `drills/` | 18 encoded strings to decode by hand. Harmless text, real encodings | Do tonight |
| `solutions/drills.md` | Answers: plaintext, CyberChef recipe, Python | Only after trying |
| `WALKTHROUGHS.md` | Three published real cases, narrated step by step, tied to drills | Tonight |
| `INTERVIEW.md` | Format, vocabulary, how to talk, report skeleton, follow-up questions | Tonight, last |
| `CHEATSHEET.md` | One page | Tomorrow, 30 min before |

## Tonight - about 3.5 hours

| Time | Do | Done when |
|---|---|---|
| 0:00-0:15 | Set up: CyberChef tab, editor with word wrap + visible whitespace, AI extensions **off**, Python REPL | You decoded Drill 01 in both tools |
| 0:15-0:45 | Read `PLAYBOOK.md` steps 0-7 slowly | You can write the 7 step names from memory |
| 0:45-1:45 | Drills 01-13, each in CyberChef **and** Python | Each under 2 minutes |
| 1:45-2:15 | Drills 14-18. Write the loop for 14 yourself | The loop runs without looking at the answer |
| 2:15-3:00 | `WALKTHROUGHS.md` with the three articles open | You can answer the 10 self-test questions |
| 3:00-3:20 | `PLAYBOOK.md` "When you are stuck" + `INTERVIEW.md` | You said the 2-minute report out loud once |
| 3:20-3:30 | Prepare for an unknown machine: download CyberChef for offline use, memorise the 4 opening questions in `INTERVIEW.md` | You can unpack a wheel with only `python -m zipfile` |

Then sleep. A rested head finds an off-screen line faster than a tired one.

**If you only have one hour:** `CHEATSHEET.md`, drills 03, 04, 10, 13, 14, 16, and Case 1.

## Tomorrow morning - 40 minutes

1. Redo drills 03, 13 and 14 cold, no notes. (10 min)
2. Pick any small legit package you know, download its wheel from pypi.org ("Download files"),
   unzip it, and read `RECORD`, `METADATA`, `__init__.py`. Follow the import chain on paper.
   Knowing what *normal* looks like is how you spot what is not. (15 min)
3. Read `CHEATSHEET.md` once. Say the 2-minute report skeleton out loud. (15 min)

## Reading list, in priority order

These are real analyses. Read at least the first three tonight; they show the actual code.

1. JFrog - LiteLLM `.pth` wheel hijack: `https://research.jfrog.com/post/litellm-hijacked-again/`
2. JFrog - agent-framework `.pth` hook: `https://research.jfrog.com/post/agent-framework-hijack/`
3. Phylum - W4SP, whitespace hiding and layered stages: `https://www.veracode.com/blog/phylum-discovers-dozens-more-pypi-packages-attempting-to-deliver-w4sp-stealer-in-ongoing-supply-chain-attack/`
4. JFrog - how malicious packages obfuscate: `https://jfrog.com/blog/detecting-known-and-unknown-malicious-packages-and-how-they-obfuscate-their-malicious-code/`
5. JFrog - obfuscation is "a signal, not a verdict": `https://jfrog.com/blog/breaking-appsec-myths-obfuscated-packages/`
6. Phylum - print instead of execute, beating an obfuscator: `https://www.veracode.com/blog/malicious-open-source-package-authors-are-bad-and-should-feel-bad/`
7. Socket - a 100-layer loop: `https://socket.dev/blog/malicious-dydx-packages-published-to-npm-and-pypi`
8. Unit42 (the one you found) - simplest setup.py stage 0: `https://unit42.paloaltonetworks.com/malicious-packages-in-pypi/`
9. JFrog - anti-debug in PyPI malware: `https://jfrog.com/blog/pypi-malware-creators-are-starting-to-employ-anti-debug-techniques/`
10. JFrog - Revival Hijack, environment-gated loader: `https://jfrog.com/blog/revival-hijack-pypi-hijack-technique-exploited-22k-packages-at-risk/`

More JFrog research: `https://research.jfrog.com/post/`. Skim two or three titles so you can say
"I read your post on X" - and mean it.

## Want real samples?

Public research collections exist. Use them only for **reading**, never running, and not on a
machine that holds your keys and tokens.

- Datadog dataset: `https://github.com/DataDog/malicious-software-packages-dataset` - PyPI samples
  under `samples/pypi/`, each an encrypted zip, password `infected`.
- pypi_malregistry: `https://github.com/lxyeternal/pypi_malregistry`
- OSSF malicious-packages (reports only, no samples): `https://github.com/ossf/malicious-packages`

Honest advice for tonight: the articles above already show the interesting code, with expert
commentary next to it. Reading three of them carefully teaches more per hour than opening raw
samples alone. Leave the datasets for after you get the job.

## What this kit is not

It does not contain fake malicious packages to dissect. The drills train the decoding, and the
three walkthroughs train the hunting on real published cases. The one thing you cannot rehearse
here is opening an unknown wheel cold - that is what tomorrow-morning step 2 is for.

## Rebuilding the drills

```bash
uv run --no-project --with cryptography python solutions/make_drills.py
```
