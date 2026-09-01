# Verify — closure and strict CONTROL

Two instruments check the class axis before any number leaves the render. Both
were repaired in session CON-1 after the DA-1 audit; each refusal below closes a
measured defect.

## V-INTEGRATED closure

`tools/vintegrated_closure.py` reads the `PAIR_COUNTS` lines the plotting macro
emits and checks, per identity:

```
sum over the eleven classes of N_OS   ==   N_OS of the M00_100 bin
sum over the eleven classes of N_SS   ==   N_SS of the M00_100 bin
sum over the eleven classes of N_trig ==   N_trig of the M00_100 bin
```

The two sides come from different routes — eleven restricted THnSparse
projections summed, against one unrestricted projection — so agreement is a real
check that the classes tile the multiplicity axis, not an identity
(`tools/vintegrated_closure.py:4-13`).

**Integer-exact, no tolerance.** The counts are unweighted for this campaign, so
the contents are exact integers in doubles. A mismatch means the classes do not
tile the sample — a dropped class, a `bins_to_ignore` entry, an off-by-one on a
boundary bin — and the fix is the axis, never an epsilon (`tools/vintegrated_closure.py:15-21`).

### The shape it asserts

The expected identity set is **derived, never hard-coded**: `PYTHIA_TUNES` times
the `associateOS` entries of
`plotting/configuration_multiplicity_HF_RUN3_V1_VINTEGRATED_CLOSURE.json`, with
every configured OS filename resolving to exactly one row of
`config/heavy_flavour_pair_registry_v1.json`. At HEAD that is three tunes × four
associates = **twelve identities**
(`tests/test_vintegrated_closure.py:62-65`).

Per identity the bin set must be exactly the eleven contract classes plus
`M00_100`, so a closing log carries twelve identities × twelve bins
(`tests/test_vintegrated_closure.py:89`).

### Six named refusals

| refusal | the defect it closes |
|---|---|
| missing or extra keys | a render that dropped a pair reduced the checked set silently, and `keys=N` never said which N |
| missing or extra bins | an eleven-class log crashed on a leaked loop variable (ledger D3) |
| duplicate `(key,bin)` | repeated identities overwrote last-wins, so a corrupt repeat could hide a correct row (ledger DA1-017) |
| nothing checked | `checked == 0` printed `EXACT keys=0` and exited 0 (ledger D4) |
| no integrated bin anywhere | rows present but no identity carrying `M00_100` raised at the summary line (ledger D3, and the final review's `NameError` path) |
| non-integral count | +0.5 and −0.5 in two classes of one identity cancel into an integral sum and passed unreported (ledger DA1-016) |

Every refusal exits nonzero (`tools/vintegrated_closure.py:22-47`).

## Strict CONTROL

`extraction/harvest_class_report.py` compares a nominal render against a control
render. The default comparator answers "did the rows we happened to share
agree?" — the right question for an integrity check over archived logs, and the
wrong one for the control that licenses the published arithmetic. A nominal of
144 rows and a control of 132 sharing **one** row satisfies it
(`extraction/harvest_class_report.py:16-19`).

`--strict-control` answers "is this the 144/132 reproduction the analysis is
defined on?" and refuses anything else by name (`extraction/harvest_class_report.py:251-253`, `:298-306`).

### The 144 / 132 / 132 shape

`strict_control_shape` derives every number from the configuration and the class
contract, so extending the pair set moves the expectation instead of leaving a
literal behind (`extraction/harvest_class_report.py:108-126`):

| quantity | derivation | value at HEAD |
|---|---|---|
| identities | tunes × configured associates | 12 |
| classes | `len(class_names())` | 11 |
| nominal rows | identities × (classes + 1) | **144** |
| control rows | identities × classes | **132** |
| shared rows | identities × classes | **132** |
| only in nominal | one integrated bin per identity | 12 |

The shape is the accepted J-c1.1 control's. This is why ruling R40's wider
figure scope stops at the figure configurations and does not reach the closure
configuration (`tools/make_variant_configs.py:165-176`); see
[RENDER.md](RENDER.md).

`tests/test_strict_control_boundary.py` asserts each refusal on its **type** and
on the CLI **exit code**, never on message text, because Python 3.10 and 3.11
word the same exception differently (`tests/test_strict_control_boundary.py:16-17`). It also asserts the
seen-to-fail direction: for the shapes the default comparator accepts, the
driver asserts that it accepts them, so the test fails if the defect returns
under another name (`tests/test_strict_control_boundary.py:11-14`).

## Receipt equality: compare the boundary payload, not `payload_sha256`

Finding F46 asks whether every configuration's render agrees on the class axis.
The boundary receipt carries a top-level `payload_sha256`, and that field is
**not** the answer. It folds per-configuration bookkeeping into the digest, so
two receipts with an identical class axis hash differently there.

RUN-N measured this on the two receipts its session produced. Their
`payload_sha256` fields differ — `ffc83232…` for V-CORRELATIONS against
`54936b31…` for V-BARYONMESON — while every quantity that defines the axis
agrees, including a per-tune `histogram_identity_sha256` of `dbdae57e…` on both.
What differs is how many pair files each configuration validated the histogram
against: `block_files_validated` 120 against 80, `central_files_validated` 12
against 8, `central_exact_comparisons` 11 against 7, and the same counts inside
`blocks[]`. Those are properties of the pair set a configuration carries, not of
the class axis.

**Check axis equality on the class-boundary payload instead.** Take each
receipt's `tunes` block, drop the five bookkeeping keys — `block_files_validated`,
`central_files_validated` and `central_exact_comparisons` per tune, plus
`files_validated` and `exact_comparisons` inside each entry of `blocks[]` — and
digest what remains. That payload keeps `histogram_identity_sha256`,
`histogram_name`, `classes`, `thresholds`, `partition` and the per-tune
fractions, which is everything the axis is made of. Both RUN-N receipts give
`2eb41c675790…` under that recipe.

`RUNN_EVIDENCE_fe3262c_20260830/gate/runn_f46.py` is the script that did it, and
it is the reference for any later check. Whether the receipt should carry an
axis-only digest of its own is post-paper design work, recorded under ruling R35
and not scheduled.

RUN-N tested two receipts, not five: three renders refused before
`WriteMultiplicityBoundaryReceipt`, which the macro calls only after every
global canvas is drawn. Five-way equality is still untested.

## What interpreter the suite has actually run under

The deployment pins **Python 3.9.16**. That is the interpreter a production
certification runs on, and the suite result that certifies a campaign is the
one measured there.

Measured on the bench by session WRAP at HEAD `6c53dc7`, with a ROOT-equipped
shell in both cases:

| interpreter | invocation | result |
|---|---|---|
| 3.14.7 (`/opt/homebrew/bin/python3`) | `tools/run_tests.sh .` | **97/97**, exit 0 |
| 3.9.6 (`/usr/bin/python3`) | `PYTHON=/usr/bin/python3 tools/run_tests.sh .` | **97/97**, exit 0 |

**The gap that remains, stated exactly.** Session HANDOFF added
`tests/test_handoff_package.py` and established its Python 3.9 compatibility
**statically** — a grammar parse, and PEP 563 deferral of its two annotations —
because it read the bench as having no 3.9. The bench does have 3.9.6, and WRAP
ran the whole suite on it, so the 3.9 *grammar* claim is now confirmed by
execution rather than by reasoning.

What is still not done is the run on the **deployment's 3.9.16**, on the
deployment, under the pinned runtime. 3.9.6 and 3.9.16 are the same language
version and different patch releases on a different machine, so the bench run
narrows the gap and does not close it. Whoever next has deployment access runs
`make test` there and records the result here.

Use `PYTHON=` to select an interpreter; the driver passes it through to every
test (`tools/run_tests.sh:60`).
