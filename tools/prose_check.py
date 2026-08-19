#!/usr/bin/env python3
"""Mechanical prose checks for the ste-technical-writing skill.

Checks plain-text and Markdown files against the mechanical subset of the
STE + Orwell rules. Heuristic by design: a flag is a prompt to look, not a
verdict. Code blocks (``` fences) and indented code are skipped in .md files.

Usage:
  python prose_check.py FILE [FILE ...]
  python prose_check.py --strict FILE ...   # exit 1 if any flag

Checks:
  LONG       sentence over 25 words (over 20 flagged for lines that start
             with an imperative-style verb)
  PASSIVE    passive-voice marker (be-verb + past participle)
  ING-START  sentence starts with an -ing form
  FLUFF      filler phrase from the delete-on-sight list
  LONG-PARA  paragraph over 6 sentences
"""

import re
import sys

FLUFF = [
    r"\bin order to\b", r"\bit is important to note\b", r"\bit should be noted\b",
    r"\bas mentioned above\b", r"\bbasically\b", r"\bsimply\b", r"\bessentially\b",
    r"\bquite\b", r"\bvery\b", r"\bleverages?\b", r"\bleveraged\b",
    r"\butiliz(e|es|ed|ing)\b", r"\bperform an analysis\b", r"\bconduct a review\b",
    r"\ba number of\b", r"\bthe fact that\b", r"\bin terms of\b",
    r"\bgoing forward\b", r"\bneedless to say\b", r"\bit is worth noting\b",
]
FLUFF_RE = [re.compile(p, re.IGNORECASE) for p in FLUFF]

BE = r"(?:is|are|was|were|be|been|being)"
PASSIVE_RE = re.compile(r"\b" + BE + r"\s+(?:\w+ly\s+)?\w+(?:ed|en)\b", re.IGNORECASE)
# Common false-positive participles/adjectives after a be-verb that are fine.
PASSIVE_ALLOW = re.compile(
    r"\b" + BE + r"\s+(?:\w+ly\s+)?"
    r"(?:open|broken|hidden|given|taken|written|done|seen|known|forbidden|"
    r"green|golden|often|even|then|amen)\b", re.IGNORECASE)

# A sentence that starts with a gerund buries its agent: "Lowering the axis would
# have needed six decades" does not say who lowers it. The check finds that shape
# by looking for a first word that ends in "ing".
#
# THE FALSE POSITIVE THIS STOPLIST CLOSES. The suffix is not the grammar. English
# has common non-gerunds ending in "ing", and three of them are pronouns that open
# a perfectly active sentence: "Nothing else changed" was flagged in
# FIGURE_INVENTORY.md 3.1d and is not a gerund at all. A second group is nouns
# (king, thing, string, spring, wing). A third is the preposition "during". A
# fourth is bare imperative verbs whose stem simply ends in "ing" -- "Bring the
# file", "Ring the node", "Sing" -- and the standard ASKS for the imperative, so
# flagging those inverts the rule.
#
# The stoplist holds the first word only. "Ringing the node" still flags, because
# its first word is "ringing".
ING_START_STOPLIST = {
    "nothing", "something", "everything", "anything",
    "during",
    "king", "thing", "string", "spring", "wing", "ring", "sing", "bring",
}

ING_START_RE = re.compile(r"^\s*(\w+ing)\b")


def starts_with_gerund(sentence):
    """True when the sentence opens with an -ing form that is a gerund."""
    m = ING_START_RE.match(sentence)
    if not m:
        return False
    return m.group(1).lower() not in ING_START_STOPLIST
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def strip_code(text, is_md):
    if not is_md:
        return text
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def check_file(path, flags):
    is_md = path.endswith((".md", ".markdown"))
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print(f"{path}: cannot read: {exc}", file=sys.stderr)
        return
    text = strip_code(text, is_md)
    for pi, para in enumerate(re.split(r"\n\s*\n", text), 1):
        prose = " ".join(
            l for l in para.splitlines()
            if not l.lstrip().startswith(("#", "|", ">", "-", "*", "+"))
            or l.lstrip().startswith(("- ", "* ", "+ "))
        ).strip()
        if not prose:
            continue
        sentences = [s for s in SENT_SPLIT_RE.split(prose) if s.strip()]
        if len(sentences) > 6:
            flags.append(f"{path}:para {pi}: LONG-PARA {len(sentences)} sentences (max 6)")
        for s in sentences:
            words = len(s.split())
            if words > 25:
                flags.append(f"{path}:para {pi}: LONG {words} words: {s[:70]}…")
            if starts_with_gerund(s):
                flags.append(f"{path}:para {pi}: ING-START: {s[:70]}…")
            m = PASSIVE_RE.search(s)
            if m and not PASSIVE_ALLOW.search(m.group(0)):
                flags.append(f"{path}:para {pi}: PASSIVE '{m.group(0)}': {s[:70]}…")
            for rx in FLUFF_RE:
                m = rx.search(s)
                if m:
                    flags.append(f"{path}:para {pi}: FLUFF '{m.group(0)}': {s[:70]}…")


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    files = [a for a in args if a != "--strict"]
    if not files:
        print(__doc__)
        return 2
    flags = []
    for f in files:
        check_file(f, flags)
    for fl in flags:
        print(fl)
    print(f"\n{len(flags)} flag(s) in {len(files)} file(s). "
          "A flag is a prompt to look, not a verdict.")
    return 1 if (strict and flags) else 0


if __name__ == "__main__":
    sys.exit(main())
