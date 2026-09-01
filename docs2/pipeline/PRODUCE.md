# Produce — campaign generation

**Historical record.** The three nominal campaigns are complete. Nothing in the
paper path re-runs this stage. Read this page to know what produced the sample,
not to produce another one.

## The command that ran

```
make submit-full CAMPAIGN=HF_RUN3_V1 ORDINAL=3 JOBS=1000 EVENTS=100000
condor_submit submit_HF_RUN3_V1_full.sub
```

`submit-full` depends on `require-ordinal` (`Makefile:203`), which refuses when
`ORDINAL` is empty and prints the four places that record ordinal claims
(`Makefile:152-177`). There is no default: the ordinal is packed into every
event identifier and into the seed band, and neither is correctable after the
jobs run (`config/campaign_ordinals_v1.json`, `purpose`).

`HF_RUN3_V1 is ordinal 3` (`config/campaign_ordinals_v1.json`, the ordinal-3
row). That row also records the campaign as sealed, `publication_eligible`
true, and the first dataset whose merged product declares
`paul_pair_objects_primary_ground_v3`.

**The README's example command names an ordinal it cannot claim** (ledger
DA1-022). `README.md:49` reads
`./hadronization render-production HF_RUN3_V2 4 1000 100000`. Ordinal 4 is held
by `HF_SYS_MUR_UP` (`config/campaign_ordinals_v1.json`, the ordinal-4 row), so
`tools/render_production_submit.py` refuses it before it writes a submit file,
and `HF_RUN3_V2` appears nowhere else in the tracked tree. A replacement needs
an owner-approved campaign and a recorded ordinal claim; nobody may invent one
in a README. Use the ordinal-3 command above.

## Every submitted job starts held

`tools/render_production_submit.py:327` emits `hold = True` unconditionally, so
a fresh campaign sits entirely held and nothing runs until an operator releases
it. Read the hold reasons before releasing.

Two hold classes look identical in a bare `condor_q` count and mean opposite
things. The submit-time parking brake carries `HoldReasonCode` 15, and the
correct action is release
(`generation/submit/Condor_README.md:54-61`, `:63-64`). A
periodic hold carries the literal marker `HF_HANG_GUARD` in its `HoldReason`,
written by `tools/render_production_submit.py:339` from
`HANG_GUARD_MARKER` (`tools/campaign.py:98`), and the correct action is retry.
That marker string, not a reason code, is what the retry path matches:
`tools/resubmit_held.py:55` reads `HoldReason` and `:271-274` splits the held
jobs on whether the marker is present.

## The seed ledger lives outside the checkout

`SEED_LEDGER` resolves to `$STATE_ROOT/seed_ledgers/burned_seeds.txt`, where
`STATE_ROOT` is `$HADRONIZATION_DATA_ROOT/project/runs` (`Makefile:35-36`). The
renderer reads that ledger and refuses any seed already burned. A ledger path
that points inside the checkout means `setupEnv.sh` was not sourced in this
shell (`Makefile:169-174`).

Seeds come from
`seed_for(tune, job_index, attempt=0, tunes=ALL_TUNES, *, campaign_ordinal)`
(`tools/campaign.py:111-117`). The campaign ordinal is what makes seeds
non-colliding **across** campaigns, not only within one.

## The hang guard, and what it is measured against

PYTHIA's junction-splitting hang is an unbounded accept-reject loop, so the job
never exits and `on_exit_hold` can never catch it
(`generation/submit/Condor_README.md:96-98`). The guard therefore watches CPU
time, not wall clock: a wedged job burns CPU continuously, a healthy job on a
contended node does not
(`generation/submit/Condor_README.md:100-105`).

The recorded per-tune attrition is 0/1000 for MONASH, 63/1063 for JUNCTIONS
(5.93 %) and 64/1064 for CLOSEPACKING (6.02 %)
(`config/cr_holdout_policy_v1.json`, `observations`). Summed, that is 127 of
3,127 attempts, **4.06 %**. `make status` computes the live rate from worker
outputs instead of quoting any of these
(`tools/campaign_status.py:264`, printed at `:271-274`).

A failed attempt promotes no ROOT file, a missing logical slot is regenerated
under a new deterministic seed, and the attrition is disclosed as measured
rather than corrected away (`config/cr_holdout_policy_v1.json`, `handling`).
Ruling R41 accepts these rates and requires the disclosure.
