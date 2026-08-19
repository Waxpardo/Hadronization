# `Validation/` — what is in there and what has actually run

**A list, not a licence.** Compiled 2026-08-10 after v38's self-review noted that
searching for M7's macro turned up `ListUnresolvedOrigins.C`, which nobody had
mentioned. **Nothing here is executed on the strength of this inventory
existing** — a run needs a named need.

**Evidence, not assertion.** "Runs" means something in the repository invokes it:
a production script, a merge/gate path, or a test. Absence of an invoker means
**no automated path**, not proof it has never been run by hand — where a manual
run is recorded in the docs, that is noted.

---

## Runs on an automated path

| macro | invoked by | what it does |
|---|---|---|
| `ValidateRawOutput.C` + `.sh` | `runCondorJob.sh`, `tests/` | per-job raw output validation; the production gate on every raw file |
| `AuditOriginResolution.C` | `runCondorJob.sh`, `tools/statistical_robustness.py` | reports unresolved origin rates per tune, in production |
| `ListUnresolvedOrigins.C` | `runCondorJob.sh` | **per-tune unresolved reporter, complementary to M7's macro.** `DESIGN_AND_RATIONALE.md:169-172`: unresolved fractions are tune-dependent and a permissive tie-break would bias exactly the comparison being made |
| `ValidatePairDirectory.C` + `.sh` | `merge_root_files.sh`, `run_status_analysis.sh`, `tools/validate_analysis_outputs.py` | the 300-file pair-directory contract; the gate's per-directory unit |
| `ValidatePairBlockClosure.C` + `.sh` | `merge_root_files.sh`, `tests/` | central == sum of the ten blocks; the closure at scale |
| `ValidateCanonicalRawManifest.C` | `tools/campaign.py`, `tools/build_canonical_manifest.py` | manifest structural validation |
| `validate_canonical_manifest.sh` | `submit_status_analysis.sh` | wrapper on the above |
| `AuditSpeciesRegistry.C` | `tests/test_pdg_species_audit.py` | species registry against the PDG reference |
| `PTHatSensitivity.C` | `tools/evaluate_pthat_sensitivity.py` | pTHat threshold sensitivity |
| `TestAnalysisRawInputContract.C` | `tests/test_analysis_raw_input_contract.py` | analysis raw-input contract |
| `TestPlotReferenceMultiplicityContracts.C` | `tests/test_plot_reference_multiplicity_contract.py` | plotting reference-multiplicity contracts |

## Run at scale for the first time this session

| macro | when | record |
|---|---|---|
| `MeasureUnresolvedSystematic.C` | **2026-08-10**, all 3000 raw files | `docs/M7_UNRESOLVED_SYSTEMATIC.md`. **Unrun since before the review; the review's M7 stood on that fact** |

## Manual run recorded in the docs, no automated path

| macro | record |
|---|---|
| `ValidateSpeciesAxisClosure.C` | `docs/SPECIES_AXIS_VALIDATION.md` — validates the 202-bin species axis against the 6-bin category axis it refines. The same cross-check the extraction reader now performs on merged output |

## No invoker and no recorded run found

**These are the ones worth knowing about.** Each is a written measurement whose
result is not in the record.

| macro | apparent purpose | note |
|---|---|---|
| `AuditTuneSettings.C` | tune settings audit | mentioned in `NIKHEF_BRINGUP.md` and `DESIGN_AND_RATIONALE.md`; no invoker found |
| `CalibrateMultiplicityAgainstMinBias.C` | *"Calibrate NCH_PRIMARY_CHARGED_\*_V1 against a published minimum-bias reference"* (own header) | **bears directly on C8**, the per-tune percentile-offset blocker |
| `TestPrimaryChargedDefinition.C` | *"Live-generator validation of NCH_PRIMARY_CHARGED_\*_V1"* (own header) | the generator-side counterpart to the above |
| `TestHardCarrierUniqueness.C` | hard-carrier uniqueness check | mentioned in `DESIGN_AND_RATIONALE.md` |
| `TestInclusiveRawKinematics.C` | inclusive raw kinematics check | bears on **B3**, the blocked inclusive-spectra path |
| `TestPlotProjectionCuts.C` | plotting projection-cut check | mentioned in `V2_PIN_SWEEP.md` |

---

## The observation this inventory exists to record

**Six written measurements have no recorded run**, and at least three of them
(`CalibrateMultiplicityAgainstMinBias`, `TestPrimaryChargedDefinition`,
`TestInclusiveRawKinematics`) bear on **open blockers** — C8's per-tune
multiplicity offsets and B3's inclusive spectra.

**That is the same shape as M7**: a macro written to answer a question, never
run, and the question therefore still open in the review. M7 took one session to
turn into a table with an uncertainty. **Whether any of these six is worth the
same treatment is an owner call, and this inventory exists so the choice is
visible rather than accidental.**

**Nothing here has been executed.**
