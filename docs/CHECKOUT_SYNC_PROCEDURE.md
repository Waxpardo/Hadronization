# Advancing the Nikhef analysis checkout

**The procedure, and the reasons each step is the way it is.** Written
2026-08-17 during the advance that ended the `43e35be8` freeze.

---

## 0. THE TWO FACTS THAT SHAPE EVERYTHING

**1. The Nikhef repository's `.git` is 23 GB.** Cloning from it is not an
option, and neither is cloning *to* it. Code moves by **git bundle over `scp`** —
tens of MB, one file, resumable, and verifiable before it is applied.

**2. Advancing is cheap; moving is not.** Advancing the checkout is a ref update
on that 23 GB object store. *Relocating* the checkout is 445 GB across a 98 %-full
NFS volume. The guard hook, the pinfile and `make can-advance` all govern the
cheap one. Any plan that treats "relocate the checkout" as a routine step has
mispriced it by four orders of magnitude (`NIKHEF_DISK_INVENTORY.md` §1.1).

---

## 1. THE GATE — `make can-advance`, and what it actually checks

Run it **on the batch node**, not the login node: `condor_q` does not exist on
the login node, and the guard's probe returns `UNKNOWN` there and refuses.

```bash
ssh -o RemoteCommand=none stbc
cd /data/alice/ipardoza/Hadronization && make can-advance
```

It checks two things, **in this order**:

| # | check | overridable? |
|---|---|---|
| 1 | **the pinfile**, `.git/checkout_pin` | **NO** — *"THE PINFILE OUTRANKS EVERYTHING, INCLUDING THE OVERRIDE"* |
| 2 | **the queue** — any in-flight job counts as pinning a commit | via `--override-reason`, which skips the queue check entirely |

> ### The override is not a general-purpose key
>
> `--override-reason` is documented for **one** shape: an advance that *restores*
> a pin rather than breaking one. It does not narrow the queue check, it
> **skips** it. Using it to get past in-flight jobs buys the advance by disabling
> the check instead of satisfying it. **Wait for the drain.** See `STATE.md`
> PENDING #12 for the improvement that would make waiting unnecessary.

### 1.1 The pinfile's removal condition was a trap, and the fix is recorded

The original pinfile named **PID `3675829`** and **`merge_v3.log`**. The
2026-08-12 reboot killed that PID and the restarted merge wrote `merge_v6.log`,
so **both clauses read as satisfied while the merge was demonstrably alive** — a
consolidation session following it literally would have advanced under a running
65 h merge. `ERROR_RECORD.md` **E8**.

**The operative condition, ratified by the second addendum:**

1. `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` **present**, *and*
2. PID **`315689`** exited cleanly — **checked on `stbc-i3`**.

**Order matters: the completion fact comes first and is authoritative.** Absence
of the PID *without* the marker is a death, not a completion — which is exactly
how the reboot produced the trap.

**The host clause is not decoration.** `ps -p 315689` run from `stbc-i1` returns
absent because the merge was on `stbc-i3`. An identity checked in the wrong
context is indistinguishable from one that has exited (E8, third facet).

Both artifacts are preserved beside where the pinfile was, and **must not be
deleted**:

- `.git/checkout_pin.superseded_20260810T230700` — the original, verbatim
- `.git/checkout_pin.removed_20260817T1817` — the refreshed version, stating the
  operative condition and the evidence it was met

---

## 2. THE ADVANCE

**Cut the bundle at advance time, not before.** A bundle cut early silently omits
whatever was committed in between — including, on this occasion, four commits
made while waiting for the queue to drain.

```bash
# 1. LOCAL -- cut the bundle from the checkout's current head to yours
cd <local physics-focus worktree>
git bundle create /tmp/advance_<date>.bundle 43e35be8..HEAD
git bundle verify /tmp/advance_<date>.bundle          # verify BEFORE shipping

# 2. SHIP
scp -o RemoteCommand=none /tmp/advance_<date>.bundle stbc:/data/alice/ipardoza/

# 3. REMOTE -- fetch from the bundle IN PLACE, then fast-forward
ssh -o RemoteCommand=none stbc
cd /data/alice/ipardoza/Hadronization
git bundle verify /data/alice/ipardoza/advance_<date>.bundle
git fetch /data/alice/ipardoza/advance_<date>.bundle physics-focus:refs/remotes/bundle/physics-focus
git merge --ff-only refs/remotes/bundle/physics-focus
```

**`--ff-only` is the whole safety argument.** The checkout is a deployment, not a
development tree: if the advance is not a fast-forward, something has been
committed *on the cluster* that is not in the bundle, and the right response is
to stop and look, never to merge.

### 2.1 Immediately after, before anything else

| check | why this one |
|---|---|
| `make test` | the suite has never run from the advanced tree |
| **hook sha verification** | the advance deploys the **fixed** installer; the deployed copy was the pre-fix one (`38e6e0a0…` → `453e3bf6…`). This is that fix's first real test, and it must run against the advanced checkout, not the scratch copy |
| guard **B-series** live | the guard itself moved (`aad9b9ad…` → `3d00494d…`) |

**Any failure: stop and report.** Do not continue consolidation work on a tree
whose suite is red.

---

## 3. WHAT MUST NOT MOVE WHILE JOBS RUN

`/data/alice/ipardoza/systematics_deploy/Hadronization` is a **separate clone**
pinned at `72ca4e39`. Every in-flight systematics job verifies that commit at
startup and refuses a tree with tracked modifications.

> **Do not check out, pull, or edit tracked files there until the campaigns
> finish.** Later commits on `physics-focus` are harmless — they are simply not
> in that deploy, which is the point.

**The two checkouts are independent by construction**, and that is why this
advance is safe while 2100 systematics jobs are in flight against the other one.

---

## 4. WHY A CLONE, NOT `git archive`, FOR DEPLOYS

The production worker's commit check is a **verification**, not a label: it
compares `git rev-parse HEAD` against the submit file's value. A `git archive`
tree has no `.git`, so it cannot be asked which commit it is — provenance in an
archived tree is **injected, never discovered**
(`HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`, the A2 pattern). A clone keeps the
guard doing its job; env injection reduces it to an assertion.

**Corollary, found by this session's reconciliation:** the
`hadronization_v3_plotting_run/` tree is a `git archive` with **no `.git` and no
injected marker**, so its commit had to be recovered by hashing 93 files against
history. It resolved cleanly (`e0b9aba` plus three files at `HEAD`), but only
because the content happened to be unambiguous. **An archived tree without an
injected commit is a provenance gap waiting to be expensive.**
