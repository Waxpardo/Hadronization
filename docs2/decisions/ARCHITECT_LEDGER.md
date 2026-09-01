# The architect's error ledger — entries #11–#18

Every entry below is a defect in how this project was *directed*, not in what
it computed. Each one was found by an executor measuring something the
architect had asserted, and each produced a rule that is now binding.

The ledger is kept because the next architect needs it. A process that cannot
name its own failure modes repeats them, and this one repeated several before
it started writing them down.

| # | the defect | the rule it produced |
|---|---|---|
| 11 | a design decision reasoned about in review but never written into the brief | write every decision into the brief, not into your head |
| 12 | a changed-file list fixed *before* the session it governed | any list a brief pins is computed at brief-writing time and stated as of that moment |
| 13 | operative commands written from memory of the environment | measure the environment; never write a command you have not resolved against the tree |
| 14 | brief lines citing artifacts never opened | open every artifact a brief cites, before locking |
| 15 | a citation verified for existence but not for enclosing scope | a `file:line` used to attribute behavior requires reading the enclosing function |
| 16 | a global changed without enumerating its consumer set | enumerate the consumer set from the tree and check every freeze gate against it |
| 17 | an identity gate written with no paired change gate | an identity proof must be paired with a gate that proves the intended change happened |
| 18 | a preservation check preserves errors | re-anchoring by content is faithful but never tests whether the anchor was ever right; a citation check must test that the anchor **supports the claim beside it** |

Entries #17 and #18 are recorded in the decision ledger for 2026-09-01 under
"Recorded, not ruled". Entries #11–#16 predate it and are recorded here.

## What #18 cost, measured

It is the most expensive entry, so it is worth stating what it actually found.
Session ARCH-1 support-checked 538 anchors and found **59** that resolved to a
real line and did not carry the construct their sentence named. It repaired 44
and recorded 15 it was not permitted to edit. Session WRAP repaired those 15,
and found **15 more** that ARCH-1's own enumeration had missed — because they
were bare `:N` anchors, which ARCH-1's search for citations *naming* the macro
could not see. The rule that fixes the second failure is R49's bare-anchor
convention; the rule that fixes the first is #18 itself.

One of the 15 recorded measurements was itself wrong: ARCH-1 recorded
`plotting/improvedPlotting_THnSparse.C:4121-4127` for a sentence about
selecting a flavour's trigger-group configuration block, and that range selects
the flavour's *directory* instead. The block is selected at `:4141-4142`. A
recorded measurement is evidence, not an answer; WRAP read every one of them
before using it.

## Candidates from WRAP, not yet ruled

These are proposed, not accepted. The architect rules on whether they enter the
ledger.

| # | the candidate defect | the rule it would produce |
|---|---|---|
| 19 | an environment property asserted absent without measuring it | a brief that says a tool is missing states the command that found it missing |
| 20 | a routed repair item described from a second-hand summary rather than from the artifact it cites | route an item by quoting the artifact, not by paraphrasing a report about it |

**#19, measured.** `BRIEF_WRAP_v2` §4.3 states that "the bench no longer has
3.9". The bench has Python **3.9.6** at `/usr/bin/python3`, and the whole suite
passes on it: **97/97**, exit 0. The gap that remains is narrower and should be
stated as what it is — the *deployment's* 3.9.16 has not run the suite — rather
than as an absence of any 3.9.

**#20, measured.** `BRIEF_WRAP_v2` §3.5 routes a `pin:` key-case defect as "a
small real defect in a tracked script", and records that the architect's own
grep could not find it. The grep was right. The defect is in a **session-local gate script in an
evidence store held outside this repository** — `runn4b_maketest.sh`, line 15,
in RUN-N4b's evidence directory — and RUN-N4b's report calls it "Cosmetic".
No tracked file greps `config/dependencies.conf` for lowercase keys. The item
was routed on a paraphrase of RUN-N4b's finding rather than on the finding,
which names the script and its status in the same sentence.
