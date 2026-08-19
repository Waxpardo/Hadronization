# Writing standard for this repository

This standard applies to all prose in this project: documentation, code
comments, commit messages, pull-request descriptions, run records, reports,
and agent outputs. It applies the writing rules of ASD-STE100 Simplified
Technical English (Issue 9) and Orwell's rules for clear writing. It adds two
substance requirements: every paragraph must add facts, and every fact must
come from the project's files or data — never from memory.

The full specification is in this directory: `ASD-STE100_ISSUE9.pdf`.
Do not read it front-to-back. Read `pdf-page-map.md` first: it maps each
section and each dictionary letter to physical page numbers. Read
`ste-rules.md` for the distilled rule set. Run `tools/prose_check.py` for the
mechanical checks.

The PDF is copyrighted by ASD. Usage rights cover universities and research
institutes. Do not commit the PDF to the published repository. It is on the
publication-export exclusion list.

## Rule precedence

Apply the rules in this order. When two rules conflict, the higher rule wins.

1. **Do not lose information.** If a rule makes a sentence less precise,
   restructure the sentence. Do not delete the substance.
2. **Substance before style.** Fix what a paragraph says before you fix how
   it says it.
3. **STE and Orwell shape every sentence.** Apply the core rules below.
4. **Break any rule before you write something unclear.**

## Core rules

- Give each word one meaning. Give each thing one name, and keep it through
  the whole document set.
- Technical nouns and technical verbs are approved vocabulary (STE rules 1.5
  and 1.12). Keep domain terms exact. Never replace a precise term with a
  vague one.
- Use short common words for general vocabulary: "use" not "utilize", "start"
  not "initiate".
- Keep instructions to 20 words or fewer. Keep descriptive sentences to 25
  words or fewer.
- Write in the active voice. Name the agent of every action.
- Put one instruction in one sentence. Write instructions in the imperative.
- Put conditions and warnings before the action they govern.
- One topic per paragraph. State the topic in the first sentence. Six
  sentences maximum.
- Use a vertical list for more than three parallel items or sequential
  actions.
- Cut every word that does no work.

## Substance tests

Apply these tests to every paragraph. Rebuild or delete a paragraph that
fails any test.

1. What fact does this paragraph add? Name it.
2. Where does that fact come from? Name the file, artifact, or measurement.
3. Would the document lose information without this paragraph? If no,
   delete it.

## Write from the artifacts

Never document from memory. Read the script before you write what it does.
Read the number from its artifact before you quote it, and cite the location.
A reader must be able to derive the prose from the repository at its current
commit.

## Commit messages

- Summary line: imperative, 72 characters or fewer. Name the object that
  changed: "Fix closure-gate call shape in merge_root_files.sh".
- Body: state what changed, why, and how it was verified. Cite tests,
  artifacts, or measurements. Active voice, standard sentence limits.
- Banned summaries: "various fixes", "minor cleanup", "updates". Name the
  changes or split the commit.

## Pull requests and reports

- Structure: what changed, why, evidence, what remains. One topic per
  section.
- Every number carries its source. Every claim of verification names the
  check that ran.
- State what was NOT done as plainly as what was done.

## Workflow

1. Read the source material for the section you will write.
2. Draft.
3. Run `python tools/prose_check.py <files>`. Fix each flag, or record why a
   flag is a false positive.
4. Apply the three substance tests to each paragraph.
5. Read the result fresh. Fix everything that makes you stop or reread.
