# Publication-export exclusions

Files in the private tree that must not leave it.

**The export session owns this list and extends it.** This session created the
file and seeded it with one entry. Any session that adds an entry states the
reason and the mechanism that enforces it.

## Why the list exists as a document

The install brief for the writing standard named a "publication-export
exclusion list (ghost check)" on 2026-08-18. No such list existed. A search
found nothing in any worktree, nothing in the Nikhef checkout, and no commit in
this repository's history containing the string "ghost". This file replaces
that absence with something a reader can check.

## Entries

### `docs/writing_standard/ASD-STE100_ISSUE9.pdf`

| | |
|---|---|
| added | 2026-08-18 |
| kind | third-party copyrighted specification |
| enforcement | `.gitignore`, verified by `git check-ignore` |
| in git history | **no** |

ASD-STE100 Simplified Technical English, Issue 9, January 2025, © ASD.
sha256 `d1f4ea9e7cd6e46b47aa9057209f99e78c0e9cfc4e27a5b07895b05c1a166431`.

Page 2 of the PDF grants irrevocable permission to use, reproduce, and publish
the document to eight classes of organization. Item 8 is "Universities and
research institutes for educational purposes", which covers this repository.
The file therefore sits inside that grant while it stays here.

A publication is a separate act. `docs/writing_standard/STANDARD.md` says do
not commit the PDF to the published repository, and
`docs/writing_standard/pdf-page-map.md` says do not redistribute it. The
`origin` remote is `github.com/Waxpardo/Hadronization`, so a commit that
carried the blob would publish it on the first push.

**The exclusion is a `.gitignore` rule rather than an export filter, and that
is deliberate.** Git history is permanent. A filter at export time cannot retract a blob that a
push has already sent. The rule therefore keeps the file out of history in the
first place:

```bash
git check-ignore -v docs/writing_standard/ASD-STE100_ISSUE9.pdf
```

`git add` on that path refuses. The file stays in the working tree, where
`pdf-page-map.md` and the Read tool reach it.

### `docs/history/**`

| | |
|---|---|
| added | 2026-08-20 |
| kind | internal session records — handoffs, audits, session logs, superseded studies |
| enforcement | **the fresh-history export**, not `.gitignore` — see below |
| in git history | **yes**, and that is what decides the mechanism |

**116 files, 2.4 MB.** Handoff chains, per-session records, repository audits and
the superseded `studies/` trees, including
`docs/history/studies/Balancing_and_Sampling/`.

**Why it must not leave the private tree.** These files record how the analysis
reached its results. They are not statements about the analysis. They quote
intermediate numbers that later sessions superseded, they record wrong turns
that later sessions corrected, and they name people and machines. **A reader
cannot tell a superseded number in one of these files from a current one**,
because the supersession lives in a different document. The published tree
carries the current documents, and `docs/REMOVALS.md`, `RENAMES.md` and
`docs/ERROR_RECORD.md` already carry the parts of the history a reader needs.

> **The mechanism is NOT `.gitignore`, and the difference matters.** The
> ASD-STE100 entry above is enforced by `.gitignore` because that file **has
> never been committed**, so a rule that refuses `git add` keeps it out of
> history permanently. **`docs/history/**` is already in every commit that
> touched it.** A `.gitignore` rule added now would change nothing: the blobs are
> in the object store and `git log` reaches them. This document says so itself —
> *"A file that is already committed needs a different remedy, and this list does
> not provide one."*
>
> **The remedy is the fresh-history export.** Publication does not push this
> repository. It builds a **new** repository from a copy of the working tree with
> the excluded paths removed, and commits it as a **single initial commit** with
> no ancestry. Nothing that is not in that one tree is reachable, so an
> already-committed path is excluded by not being copied, rather than by a rule
> that refuses to add it.

**The command that shows the mechanism working**, run against the export tree
before the first push:

```bash
test -z "$(git -C "$EXPORT" ls-files -- 'docs/history')"   && test "$(git -C "$EXPORT" rev-list --count HEAD)" = 1   && echo EXPORT_CLEAN
```

Neither clause alone is enough. The first says the path is
absent from the export's tree. The second says the export has no ancestry for it
to survive in. An export that failed the second clause would carry every
excluded file in its history no matter what its tree contained.

> ### ⚠ The export tool does not exist yet, and this entry does not pretend it does
>
> No script in this repository builds the export. Searched 2026-08-20 across
> `tools/`, `Makefile` and `extraction/`: nothing constructs a publication tree.
> **This entry specifies the mechanism and its check; it does not record a
> working one.** The check above is the acceptance test the export tool must
> pass, written now so the tool is built against a stated contract rather than
> the contract being written to match whatever the tool does.
>
> **Until that tool exists, the exclusion is a rule with no enforcement.** That
> is the honest status, and it is recorded here rather than in a commit message.

---

## How to add an entry

1. State the path, the date, and what kind of file it is.
2. State why it must not leave the private tree.
3. Name the mechanism that enforces the exclusion, and the command that shows
   the mechanism working.
4. Say whether the file is already in git history. A file that is already
   committed needs a different remedy, and this list does not provide one.
