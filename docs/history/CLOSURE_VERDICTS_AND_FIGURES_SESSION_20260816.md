# Both closures PASS, the table is FINAL, and the figure set runs three-tune — 2026-08-16 (nineteenth session)

**Suite 45/45 → 46/46** (two tests added). Wall clock 15:04–16:05 CEST.
`stbc-i3` up **3 d 15 h 57 m**, boot 2026-08-12 23:07 — **no reboot**, so the
brief's relaunch contingency did not apply.

> **Headline: JUNCTIONS and CLOSEPACKING both PASSED closure, so
> `docs/THREE_TUNE_CENTRAL_TABLE.md` is FINAL — the resubmission's central
> number exists. Fig 1's reserved slots are filled and Paul's stack now runs
> three-tune on v3 with the ratio canvases. One pre-registered expectation
> remains unmet and is recorded at the top of the table rather than buried.**

---

## 1. Task 1 — the verdicts. Both PASS.

Both closures finished while the previous session was closed. **JUNCTIONS
2026-08-16 11:58:20 CEST after 13 h 50 m; CLOSEPACKING 11:37:27 after 13 h
29 m** — both inside the 14:10–14:20 estimate.

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3 central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=2100 additive_metadata_closure_checks=3600 invariant_metadata_checks=1500 source_filter_contract_checks=300 expected_central_events=100000000 relative_tolerance=2e-10
```

**Identical field for field between the two tunes.** 2100 / 1500 as
pre-registered, schema v3, errors 0, tolerance 2e-10 — **not** the 1800/600
v2-sidecar failure mode.

**Checked three ways, not one.**

1. `harvest_tune.py --stage closure` on each log — rc 0, "matches the
   pre-registration". The counts were not eyeballed.
2. **The schema was verified by reading the emitted value**, because the A4
   argument does not exist on the frozen tree. Recorded as a deliberate method,
   not an omission.
3. **The wrapper's own gate, inferred from what is absent.** Its failure branch
   writes `RETAINED closure log for diagnosis` to stderr unconditionally, and
   both runs had stderr in these logs. Neither log contains it, so both took the
   success path — an independent confirmation of exit 0 for two detached
   processes whose status no shell held.

**And the merge corroborated MONASH independently**: its own sequential pass
reached `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=MONASH` at 12:39 with an
identical summary line, from a separate process reading the same directories.

### The table was promoted, and one thing was not swept up with it

`THREE_TUNE_CENTRAL_TABLE.md` is FINAL: both verdict lines verbatim in a new
§0b, the ⛔ struck, `STATE.md` and `GOLDEN_OUTPUTS.md` §2.9c updated with the
digest and a regeneration recipe. **No number moved on promotion** — they were
measured before the verdicts and the regenerated table is byte-identical to the
provisional run.

> **`PER_TUNE_PROCESSING_PREREGISTRATION.md` step 2 registers I2 = zero flagged
> bins and says a step-2 failure stops that tune's step 3. JUNCTIONS has three
> flags and CLOSEPACKING one.** They are diagnosed, confined to bins that
> framing predates, and jackknifed immaterial at under 1.19 SEM — but the
> expectation is unmet, and **this promotion was scoped to the closure verdicts
> because that is what the brief gated it on.** That is a scoping decision, not
> a measurement, and it is now stated at the top of the table, in STATE.md's
> pending list and in GOLDEN_OUTPUTS §2.9c. **The owner's ruling is the one
> open item.**

## 2. Task 2 — nothing to do yet, and the watcher is correctly still armed

The merge is **alive and inside its own JUNCTIONS closure** (~2.5 h in at
session end, one pass done). `CANONICAL_PAIR_BLOCK_CLOSURE_PASS
tune=CLOSEPACKING` has **not** appeared, so the EOL watcher has not fired —
which is correct, not a misfire. Supervisor at **0 restarts** since 2026-08-14.

**Merge completion is ~22 h away**, so STATE.md does **not** say the campaign is
complete; it says all 33 legs are merged and all three closures passed, with the
merge still running its redundant pass. **The freeze stands**: pinfile intact,
checkout unmoved at `43e35be8` and tracked-clean, stale partial untouched at its
Aug 12 mtime.

## 3. Task 3 — the figure set

### 3a. Fig 1's reserved slots filled

The JUNCTIONS and CLOSEPACKING anchors are committed, so
`make_paper_figures.py` draws three bars per group and the legend no longer says
"not yet merged". The generator's docstring promised no layout change was
needed; **that was true of the bars and false of panel B**, whose row set was
one tune's top-8 — MONASH's carries B±, the CR tunes' carries Λ_c — so three
top-8 lists would have put different observables in one bar group under a single
label. It now uses the table's common row set.

**All 42 cells — every mean and every SEM in both panels — were checked against
the FINAL table. Zero mismatches.**

**Committing the anchors bought more than the figure:** the three-tune table now
regenerates from the repository alone, and its stdout digest from the committed
anchors is **byte-identical** to the one from the remote run roots. The suite
asserts every structural cell and that digest.

### 3b. Three layout defects, all found by rendering and looking

None was visible to the suite.

- **fig 1 panel A**: three value labels per group at one height collided once
  all three tunes were present (`39.94 40.00`, `0.0000 0.05 0.06`).
- **fig 1 panel B**: −30° labels overran their 36 px slots and the caveat box is
  drawn *after* them, so `Lambda_c+` rendered as `c+`. The box moved rather than
  the names being shortened — they must match the table's rows.
- **fig 3**: staggered boundary labels drawn through the panel title, and a
  residual box 3 px too short so its last line fell outside it. Moving the panel
  down exposed a third — the box then covered panel B's per-class values. **Its
  numbers did not change**, and it is in a figure this brief did not name; fixed
  because the standing rule is that every figure is looked at before it is
  committed, and looking is what found them.

### 3c. Paul's stack, three-tune on v3

Configuration **generated, not hand-copied** —
`plotting/make_hf_run3_v1_three_tune_config.py`, ten canvases (three yield rows
plus two CR/MONASH ratio rows, beauty and charm), with
`tests/test_three_tune_plot_config.py` asserting `--check` and pinning
`bins_to_ignore == []` on every canvas.

**The B6 axis assertion now runs over three tunes**: `tunes_compared=3`,
`identical_across_tunes=PASS`, 36 boundary lines in three identical tables,
every value equal to the committed artifact. It could previously be asserted
over one tune, then two.

**Cross-checks against the FINAL table, per tune, all agreeing:**
`pair_registry_sha256 = ea9b0232…` — the same artifact the extraction used — and
`regular_bin_integral = 100,000,000`, the count the closures asserted. 24
central and 240 block files validated; partition coverage and disjointness PASS
for all three.

Full record: `docs/plotting_validation/hf_run3_v1_threetune_20260816/`.

### 3d. A latent macro bug only three tunes could expose

`drawBalancingPlots` set its x-axis bin labels under `if (i==0)`, where `i`
indexes the **global** tune list while the loop `continue`s past tunes not on
the canvas. A canvas whose only tune is JUNCTIONS never reached the branch and
rendered with a bare numeric 0–2 axis. Labels appeared on the MONASH row and on
the two ratio rows — which carry MONASH as denominator, hence `i==0` — and
nowhere else.

**No earlier configuration could show it**: each had one tune globally or MONASH
first on every canvas. The guard is now a per-canvas flag set after the first
*drawn* tune, which is what its own comment always intended.

**Then the receipt guard fired, and was right to.** The receipt pins
`plotter_source_sha256`; the fix moved it while the boundary values were
unchanged. Run 1's receipt is preserved rather than deleted, and run 3 wrote the
consistent one. **A publication-grade run starts from a clean output directory.**

### 3e. What the figure is not

Recorded plainly rather than left for a reviewer: **no panel names its tune**
(three yield rows distinguished only by colour, no key), the legend takes about
a third of every panel and repeats "(CLOSEPACKING/MONASH)" eleven times, and
**the ratio y-range 0.2–5 is mine and too wide** for structure that sits between
~0.6 and ~3. That is figure design, and the B6 ruling puts it with whoever owns
the paper figure. Two x-bins per panel is **correct**, inherited from the v3
configuration's two associate configurations per flavour.

## 4. Commits

| | |
|---|---|
| `923e11b` | both closures PASS; the table is FINAL |
| `114cdf4` | fig 1's reserved slots fill; layout defects found by looking |
| `bac8d9b` | Paul's stack runs three-tune on v3; the latent label bug |

## 5. For the next session

1. **The owner's ruling on the I2 flags** — the one open item on the FINAL
   table. A category-aware null is the obvious follow-up and is **not** a change
   to make quietly: retuning a null until it stops flagging is how a real defect
   gets normalised away.
2. **Merge completion, ~13:00 Aug 17.** When `CANONICAL_PAIR_BLOCK_CLOSURE_PASS
   tune=CLOSEPACKING` appears, verify the EOL watcher stopped the supervisor
   rather than letting it restart a finished merge, then record the campaign
   COMPLETE in STATE.md. **The freeze lifts in the consolidation phase, not
   there.**
3. **The figure design in §3e**, if the paper wants these canvases.
