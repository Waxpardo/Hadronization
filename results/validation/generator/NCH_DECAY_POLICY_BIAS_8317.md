# The decay-policy N_ch bias, re-measured on PYTHIA 8.317 — 2026-08-17

**Supersedes** the 1.3 % figure in `NCH_CALIBRATION_20260730.md` §Conclusions 2
and in the design record §3.5, both of which are **8.315** measurements.
**On 8.317 the bias is 0.767 %, not 1.327 %.** The design record went internal
on 2026-08-22. `NCH_CALIBRATION_20260730.md` preserves the 8.315 values, 7.007
and 6.914, in the tree. The fuller dated design record is preserved in the
internal archive.

**Question answered:** by how much does the production decay policy (heavy hadrons
stable) undercount primary charged multiplicity relative to the experimental
primary definition, *on the generator production actually uses*?

## Why it was re-measured

The number is load-bearing twice over. It is the one consequence of the decay
policy the paper is required to state
(the design record §3.5, quoted here as "The production decay policy costs
1.3 %"),
and it is the **entire input** to systematic source S5
(`docs/SYSTEMATICS_PREREGISTRATION.md` §7), whose null holds only while the bias
stays below the margin that separates a class boundary from the nearest integer.

On the 8.315 value that margin was a factor of **1.16** — 1.327 % measured
against the 1.538 % that would move `c11`'s edge at `N_ch = 32.5`. A 16 % margin
on a superseded generator version is not a null anyone should rely on.

## Method

`Validation/CalibrateMultiplicityAgainstMinBias.C`, unmodified, **200 000 events
per arm** (ten times the 20 000 the 8.315 measurement and the pTHat scan used),
`SoftQCD:inelastic`, 13.6 TeV, INEL>0. **Both arms use the macro's fixed seed
`20260730`**, so they generate the same underlying event sequence and the
comparison is **paired** — the shared event content cancels, and the difference is
far better determined than either mean's own standard error.

```bash
source ./setupEnv.sh
root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(200000,false,10.0,false)'
root -l -b -q 'Validation/CalibrateMultiplicityAgainstMinBias.C(200000,false,0.01,true)'
```

Run on `stbc-i1`, deliberately not `stbc-i3`, which was carrying the merge.

## Result

`dN_ch/dη`, MB convention (`|η| < 0.5`, `pT → 0`, heavy inclusive):

| arm | `tau0Max` | heavy decays | INEL>0 accepted | `dN_ch/dη` |
|---|---|---|---|---|
| experimental convention | 10 mm | **on** | 172 825 | **7.040** |
| exact production policy | 0.01 mm | **off** (118 entries) | 172 429 | **6.986** |

> ## THE BIAS IS 0.767 % ON 8.317, against 1.327 % on 8.315
>
> (7.040 − 6.986) / 7.040 = **0.767 %**. The production counter undercounts by
> that much, because the experimental primary definition counts charm/beauty decay
> daughters — open-heavy hadrons have `cτ₀ < 1 cm` — and production disables those
> decays.

**The bias fell by 42 %.** Both arms rose relative to 8.315 (7.007 → 7.040 and
6.914 → 6.986), but the *production-policy* arm rose four times as much, which is
what shrank the gap.

### Every counter, both arms

| counter | experimental convention | production policy |
|---|---|---|
| `\|η\|<0.5`, `pT>0`, heavy incl. | 7.040 | 6.986 |
| `\|η\|<0.5`, `pT>0.15`, heavy incl. | 6.454 | 6.406 |
| `\|η\|<0.5`, `pT>0.15`, heavy **excl.** | 6.454 | 6.389 |
| `\|η\|<1.0`, `pT>0.15`, heavy excl. | 13.068 (`dN/dη` 6.534) | **12.948** (`dN/dη` 6.474) |
| `\|η\|<4.0`, `pT>0.15`, heavy excl. | 51.686 (`dN/dη` 6.461) | **51.201** (`dN/dη` 6.400) |

**Two internal consistency checks pass.** In the experimental-convention arm the
`heavy incl.` and `heavy excl.` rows are *identical* (6.454 both) — correct, since
with decays enabled no heavy hadron is final, so excluding them removes nothing.
In the production-policy arm they differ by 0.017, which is the stable heavy
hadrons themselves being counted.

**The counter still reproduces the published reference**: ALICE 13 TeV INEL>0
`6.94 ± 0.10`, expectation ~7.0–7.1 at 13.6 TeV. The macro's own verdict line is
`counter reproduces the minimum-bias reference`.

## Consequences

### 1. S5's null is comfortable rather than fragile

`c11` at `N_ch = 32.5` needs a **1.538 %** shift to cross an integer. At 0.767 %
the margin is a factor of **2.01**, not 1.16. Every other boundary clears by more.
`docs/SYSTEMATICS.md` §2 and the recorded result are updated; the boundary above
which this bias *would* migrate a class moves from 37.7 to **65.2**, far outside
any plausible re-binning of an axis whose widest boundary is 32.5.

### 2. The paper's number changes

The design record §3.5 and `NCH_CALIBRATION_20260730.md` both state 1.3 %. **On the production generator it is 0.77 %.** The sentence must change, or
be dropped — the same disposition `PTHAT_MULTIPLICITY_SCAN_8317.md` reached for the
"36 % below minimum bias" claim it superseded.

### 3. The two `|η|` counters are now measured together on 8.317

`51.201 / 12.948 = 3.954`, and per unit η the two agree to **1.1 %** (6.474 vs
6.400). That is the input systematic source **S4** needs for its
percentile-preserving boundary translation, measured on the production generator
rather than inferred.

## Limits

- **200 000 events per arm, one seed.** The pairing makes the *difference* precise,
  but the two arms' INEL>0 acceptances differ by 396 events (0.23 %) because the
  decay policy changes `N_ch` near the ≥ 1-charged threshold, so the pairing is not
  exact. The residual is small compared with the factor-2 margin it has to clear.
- **MONASH only**, as in the 8.315 measurement. The CR tunes' decay policy is
  identical, and the bias is a property of the policy rather than of the
  fragmentation, so no per-tune difference is expected — but that is an
  expectation, not a measurement.
- This measures the bias on **minimum bias**. The production sample is
  hard-heavy-flavour, where the heavy-hadron content per event is far higher, so
  the bias there is plausibly *larger*. **Not measured**, and S5 uses the MB
  number — which is the conservative direction only if the hard-sample bias is
  smaller, so this is a real open edge, recorded rather than resolved. It would
  become material if the class axis were ever re-binned above `N_ch ≈ 65`.
