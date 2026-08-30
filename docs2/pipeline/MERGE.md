# Merge — the supervised canonical merge

Ruling R25 wires `tools/merge_supervisor.sh` into the launcher. The merge runs
supervised; it is not invoked bare.

## The command

```
./hadronization merge hf_run3_v1_candidate v3
```

The pair schema defaults to `v3` (`hadronization:288`). The launcher resolves
the dataset first, so an unknown key stops before anything is arranged
(`hadronization:73-91`).

Before launching, the launcher captures two values and passes them to the
supervisor as expectations: `HEAD` at launch, and the sha256 of the resolved
canonical manifest (`hadronization:291-300`). It then runs the supervisor
through `tools/launch_with_reset_signals.py` with eight positional arguments
(`hadronization:301-307`, signature at `tools/merge_supervisor.sh:6-8`).

## What the supervisor refuses, and why it exists

The motivating record is the smoke run that lost its child's exit status: a
merge that failed reported success to its caller. Every refusal below is a
named line in the run log and a nonzero exit
(`tools/merge_supervisor.sh:118-177`):

| refusal | condition |
|---|---|
| `REFUSAL_INTERPRETER_UNAVAILABLE` | the Python command does not resolve |
| `REFUSAL_MERGE_DRIVER_UNAVAILABLE` | `merging/merge_root_files.sh` is absent |
| `REFUSAL_WATCHER_UNAVAILABLE` | the end-of-log watcher is absent |
| `REFUSAL_SESSION_LAUNCHER_UNAVAILABLE` | the session launcher is absent |
| `REFUSAL_CHECKOUT_DIRTY` | the checkout has uncommitted changes |
| `REFUSAL_HEAD_CHANGED` | `HEAD` moved after launch |
| `REFUSAL_MANIFEST_UNAVAILABLE` | the canonical manifest cannot be read |
| `REFUSAL_MANIFEST_CHANGED` | the manifest sha256 moved after launch |

A pass prints `PRECHECK_PASS` with the head and manifest digest it accepted
(`:177`).

## Completion is proved twice, not once

A clean child exit is not enough. The supervisor requires **both** a zero exit
status **and** the final marker
`CANONICAL_SUPERVISED_MERGE_COMPLETE output_tag=<CAMPAIGN>` in the run log
(`:40`, `:244-249`). A zero exit with no marker is `FAIL missing_final_marker`.

Restarts are bounded and only for signals. A child exit status outside 129–192
is a deterministic refusal and is never restarted
(`FAIL deterministic_child_exit`, `:254-256`); a signal exit restarts up to
`MAX_RESTARTS`, default 2 (`:35`, `:259-265`).

The supervisor also checks that the attempt's whole process group is gone
before it judges the attempt (`FAIL lingering_attempt_process_group`, `:236`),
which is the check the lost-exit-status episode showed was missing.

## The closure gate runs inside the merge

`merging/merge_root_files.sh:315-319` calls
`Validation/validate_pair_block_closure.sh` per tune and fails the merge on a
nonzero status, retaining the staged report (`:320-322`). The gate takes the
campaign pair schema as an explicit argument and has no default (`:52-60`).

What the gate asserts, and the row shapes it asserts them on, is in
[VERIFY.md](VERIFY.md).
