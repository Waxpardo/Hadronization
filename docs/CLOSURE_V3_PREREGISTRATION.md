# Closure at v3 scale — the count table, derived before the run

**The v2 count table is wrong for v3 output, and it fails in the direction that
looks like success.** This file derives the v3 numbers from
`config/pair_file_object_contract_v1.json` rather than restating them, and puts
the inversion beside them so no reader carries the old table forward.

---

## THE NUMBERS

| | **v3 (correct)** | v2 (the trap) |
|---|---|---|
| **content comparisons** | **2100** = 7 × 300 | 1800 = 6 × 300 |
| **invariant comparisons** | **1500** = 5 × 300 | 600 = 2 × 300 |

> ### ⚠ IF A v3 CLOSURE RUN REPORTS 1800 / 600, IT IS BROKEN — NOT PASSING
>
> Those are the **v2** numbers. A v3 run that produces them has resolved the
> object set against the wrong schema, which means **`hFlavourClosureSpecies` was
> never closure-checked and the three species provenance strings were never
> identity-checked** — precisely the objects the whole v3 exercise exists to
> validate. The run would complete, report no failures, and have skipped the new
> content. **Check the counts before believing the verdict.**

---

## THE DERIVATION

Both counts are `n_objects × 300 pair files`. What varies is which objects
qualify, and the contract answers that in two different ways for the two
questions.

### Content: `closure == "checked"` AND a histogram-like `root_class`

Closure here is the ten-block sum rule — central equals the sum of the ten
disjoint blocks — so it applies to objects that *accumulate*: `THnSparse`,
`TH1D`, `TProfile`. Scalar counters are `closure: checked` too, but they are
compared as numbers, not as binned content, and are not in this table.

| | v2 | v3 |
|---|---|---|
| `hAsKinematics` | ✓ | ✓ |
| `hCorrelations` | ✓ | ✓ |
| `hCorrelationsByOrigin` | ✓ | ✓ |
| `hFlavourClosure` | ✓ | ✓ |
| **`hFlavourClosureSpecies`** | — | **✓ (`since_schema: v3`)** |
| `hTrKinematics` | ✓ | ✓ |
| `summed MULTIPLICITY` | ✓ | ✓ |
| **total** | **6 → 1800** | **7 → 2100** |

**One object moves the number, and it is the 202-bin species sparse.**

### Invariant: `identity_checked == "true"`

A different assertion, and the contract is explicit about why it is distinct:
closure says *central equals the sum of the blocks*; identity says *the central
file and all ten blocks carry an **identical** value*. An invariant has nothing
to sum — but blocks disagreeing about a contract string would mean the sum was
taken over objects that do not mean the same thing.

| | v2 | v3 |
|---|---|---|
| `associate_origin_category_labels` | ✓ | ✓ |
| `associate_origin_category_schema` | ✓ | ✓ |
| **`species_ordinal_schema`** | — | **✓** |
| **`species_ordinal_labels`** | — | **✓** |
| **`species_ordinal_digest`** | — | **✓** |
| **total** | **2 → 600** | **5 → 1500** |

**The invariant count more than doubles**, because v3 added three provenance
strings that travel with the species axis — including the digest
`646f310f78126267`, which is what makes the ordinal table legible in-file.

**This is why the ruling calls the table inverted rather than merely changed:**
the smaller v2 numbers are not a subset of a larger v3 check on the same
objects. Both counts grow, and they grow for *different reasons* — one new
content object, three new provenance strings.

---

## PRE-REGISTRATION

| # | prediction |
|---|---|
| **C1** | Content comparisons = **2100** exactly. |
| **C2** | Invariant comparisons = **1500** exactly. |
| **C3** | Zero closure failures and zero identity failures across all 3000 → 300 merged directories. |
| **C4** | The run resolves the object set from each file's **own** `analysis_schema` (`…_v3`), not the sidecar JSON, which still reads `…_v2` — see `HANDOFF_20260809_v31.md` §5. **If the counts come back 1800/600, this is the first thing to check.** |

**Derived from the contract on 2026-08-09 at `1de9bfe`**, reproducible with the
counting rules above. Any future contract edit that adds a closure-checked
histogram or an identity-checked string moves these numbers, and the derivation
should be re-run rather than the numbers re-quoted.
