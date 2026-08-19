# ASD-STE100 writing rules, distilled

Official section names (Issue 9): 1 Words · 2 Multi-word nouns · 3 Verbs ·
4 Sentences · 5 Procedural writing · 6 Descriptive writing · 7 Safety
instructions · 8 Punctuation and word count · 9 Writing practices · General
recommendations GR-1–GR-8 (GR-7 inclusive language and GR-8 possessive form
are new in Issue 9). The headings below follow this structure.

This file distills the writing rules (Part 1) of ASD-STE100 Simplified
Technical English, Issue 9 (2025-01-15), for use on technical and research
prose. It is a working summary, not the specification. Where this file and the
official specification differ, the specification governs. The official PDF is
in this directory (`ASD-STE100_ISSUE9.pdf`) with a page map
(`pdf-page-map.md`): use the map to read only the pages you need. Part 2 of
the PDF is the dictionary of approved general words with one approved meaning
each; this file does not reproduce it — check disputed words there
(UPPERCASE = approved).

STE was written for aerospace maintenance documentation. Research prose needs
more descriptive range than a maintenance manual. Apply the rules below with
the precedence order from SKILL.md: information first, substance second, rules
third, clarity above all.

## 1. Words

- Use a word in one part of speech and one meaning. "Test" as a noun OR as a
  verb inside one document set — do not use "test" to mean both the procedure
  and the criterion.
- Use the same term for the same thing everywhere. Synonym variation is for
  literature, not for documentation. If the object is a "block", it is never
  later a "chunk" or a "segment".
- Technical nouns are allowed (rule 1.5): names of tools, particles, files,
  parameters, algorithms, quantities, and standards. Keep them exact. (Issue 9
  uses "technical noun"; older issues said "technical name".)
- Technical verbs are allowed (rule 1.12): domain actions with no plain
  equivalent ("merge", "hash", "commit", "fit").
- For everything else, prefer the short common word. Typical swaps:
  "use" (not utilize/employ), "start" (not initiate/commence), "end" (not
  terminate), "show" (not demonstrate/illustrate, when showing is meant),
  "need" (not require, when need is meant), "about" (not approximately, in
  running prose), "do" (not perform, when do is meant).
- Do not use vague quantifiers where a number exists. "Three campaigns", not
  "several campaigns".

## 2. Noun clusters

- Keep noun clusters to three nouns or fewer. Break longer clusters with
  prepositions: "the receipt for the boundary of the multiplicity class", not
  "the multiplicity class boundary receipt" — unless the cluster is an
  established technical name. Established names stay intact and consistent.
- When you must introduce a long technical name, define it once, then use it
  unchanged.

## 3. Verbs

- Use the active voice. Name the agent of every action. Passive voice hides
  who does what, and in procedures that hiding causes errors.
- Allowed exception: when the agent is truly unknown or irrelevant AND the
  sentence is descriptive, the passive may stand — but try the active first.
- Use simple tenses: past, present, future. Avoid perfect and continuous
  forms where a simple tense carries the meaning.
- Prefer a finite verb to an "-ing" form: "the script that validates", not
  "the validating script"; "after the merge ends", not "after finishing the
  merge".
- Use the imperative for every instruction.

## 4. Sentences

- Procedural (instruction) sentences: 20 words maximum.
- Descriptive sentences: 25 words maximum.
- One topic per sentence. One instruction per sentence.
- Do not omit words that show structure ("that", "the") if omitting them can
  cause a misread.
- Connect sentences with explicit logic words when the relation matters:
  "because", "therefore", "but", "then".

## 5. Procedures

- Imperative mood, one action per step.
- Order steps in the order of execution.
- Put the condition before the action: "If the gate refuses, check
  DATASET_SELECTOR", not "Check DATASET_SELECTOR if the gate refuses".
- Put warnings and cautions before the step they protect.
- Never bury an instruction inside a descriptive paragraph. Pull it out into
  a step.

## 6. Descriptive writing

- One topic per paragraph. The first sentence states the topic.
- Six sentences maximum per paragraph.
- Present information in the order the reader needs it: what it is, what it
  does, how to use it, what can go wrong.
- Use a vertical list when you present more than three parallel items or more
  than three sequential actions.
- Tables for data. Prose for reasoning. Do not write a table in sentence form.

## 7. Warnings, cautions, notes

- A warning protects people. A caution protects equipment or data. A note
  gives information. Do not mix the three.
- Start with the condition, then the command: "The live merge reads this
  checkout. Do not run git commands here until the merge exits."
- Make the consequence explicit when it is not obvious.

## 8. Punctuation and layout

- Use punctuation to show structure, not decoration.
- Use a colon to introduce a list. Use semicolons sparingly; a period and a
  new sentence is usually clearer.
- Hyphenate noun clusters only when the hyphen prevents a misread.
- Keep list items grammatically parallel.

## 9. Writing practices

- Define every abbreviation at first use, then use it consistently.
- Numbers: use digits for measured values, counts, and identifiers.
- Units and symbols: exact and consistent ("GeV/c", not "GeV/c" one place and
  "Gev" another).
- Cross-reference by stable identifier (file path, section number, commit
  hash), not by "above" or "below".
- Date every statement whose truth can change, or tie it to a commit.

## Orwell's six rules

1. Never use a metaphor, simile, or figure of speech you are used to seeing
   in print.
2. Never use a long word where a short one will do.
3. If it is possible to cut a word, cut it.
4. Never use the passive where you can use the active.
5. Never use a foreign phrase, a scientific word, or a jargon word if you can
   think of an everyday equivalent. (Domain terms with no equivalent stay.)
6. Break any of these rules sooner than say anything outright barbarous.

## Fluff patterns to delete on sight

"in order to" → "to" · "it is important to note that" → (delete) · "it should
be noted that" → (delete) · "as mentioned above" → cross-reference or delete ·
"basically" / "simply" / "essentially" → (delete) · "quite" / "very" /
"rather" → (delete or quantify) · "leverage" → "use" · "utilize" → "use" ·
"perform an analysis of" → "analyze" · "conduct a review of" → "review" ·
"a number of" → the number · "the fact that" → restructure · "in terms of" →
restructure · "going forward" → (delete) · "robust" without a stated failure
mode → state the failure mode it survives.
