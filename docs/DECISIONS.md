# Authoritative project decisions

**Recorded:** 2026-08-22  
**Status:** active rebuild contract

## D1 — Tune-local multiplicity percentiles

Multiplicity classes are the top-percentile windows `90-100, 80-90, ...,
1-10, 0-1%`. Each tune resolves every edge from its own merged
`summed MULTIPLICITY` distribution. The same percentile label therefore
selects the same activity fraction, not necessarily the same absolute `N_ch`,
across tunes.

This restores the scientific definition used by the workflow merged in Paul
Veen's GitHub PR 13 (`11884cf1ad3613e8e6997bbff32d48a3e7d89570`). The rebuild
does not restore old implementation defects: boundary integers are assigned
once, the classes are required to be disjoint and exhaustive, missing
thresholds do not fall back to an axis endpoint, and all pair inputs must carry
an identical tune-level multiplicity histogram.

The separate MONASH minimum-bias sample remains useful calibration evidence;
it is not a class-definition source.

## D2 — Recorded CR attempt attrition is accepted

The nominal accounting observed 0/1000 discarded MONASH attempts, 63/1063
JUNCTIONS attempts (reported as 5.93%), and 64/1064 CLOSEPACKING attempts
(reported as 6.02%). Supervisors accepted this approximately-six-percent CR
attrition.

Acceptance does not change the data path. A failed attempt promotes nothing;
the logical slot is retried with a new deterministic seed; only complete files
in the sealed canonical manifest enter the analysis. The attrition stays in
the provenance and is not corrected away. This decision applies to the
recorded campaigns and is not a generic future threshold.

## D3 — Nikhef-first, laptop-optional execution

Nikhef is the complete execution environment and owns large campaign data. A
local clone is used to develop and test source, but no production artifact or
workflow transition depends on the Mac. Site profiles and dataset selectors
resolve storage independently of checkout location.

## D4 — Clean source of truth

This rebuild starts from the deterministic public source projection, not by
merging the divergent working, harvest, and publication histories. Those
repositories remain read-only provenance. The external Nikhef campaign bytes
are reused only through manifests and validation; they are not copied into Git.

New changes land here first, pass portable checks, pass the pinned Nikhef
checks, and are then promoted as the single main repository.
