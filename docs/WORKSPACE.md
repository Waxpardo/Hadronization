# Workspace, dependencies, and machine-specific paths

Everything a machine needs, and every path that only works on one machine, in
one place.

The rule this repository follows: **no tracked file contains a path that only
works on one machine.** Machine-specific values live in
`config/dependencies.local.conf`, which is untracked. If something does not
resolve, `make doctor` will say so and name the variable to set.

```bash
make doctor
```

---

## Quick start on a new machine

```bash
make setup     # creates config/dependencies.local.conf from the example
make doctor    # tells you exactly what is unresolvable here
make build     # builds the producer (needs ROOT + PYTHIA)
make check     # doctor + tune cards + registry + tests
```

---

## What the repository needs

| Component | Version | Why pinned |
|---|---|---|
| PYTHIA | 8.317, stock upstream | 8.316 fixed trial-hadron generation in `StringFragmentation::kinematicsHadronTmp`, used by the close-packing framework. CLOSEPACKING is one of the compared tunes, so 8.315 means running known-buggy code. |
| ROOT | 6.30.01 (ALICE CVMFS) | Analysis, plotting, and all `Validation/*.C` macros run through ROOT/ACLiC. |
| GCC toolchain | 14.2.0 for PYTHIA/producer, 12.2.0 for ROOT | The CVMFS ROOT package was built against 12.2.0 and the PYTHIA side against 14.2.0. They are deliberately different. |
| Python | 3.11+ | Standard library only. No third-party packages, no virtualenv. |
| HTCondor | any | Only `condor_submit` is needed, and only to queue. Submits can be rendered anywhere. |

PYTHIA is built from the official tarball, unmodified, with `-std=c++20`:

```
https://pythia.org/releases/pythia83/pythia8317.tgz
sha256 1ae551d14dac495ddfe6b344792035ebe410fe6c6004d44a335e0ece0e745adf
```

`-std=c++20` is not a preference. ROOT's `--cflags` appends `-std=c++20` to the
producer's compile line, and GCC honours the last standard flag given, so the
producer is C++20 regardless of what the Makefile says. PYTHIA is built to
match deliberately rather than by accident.

**Versions are asserted, not assumed.** `setupEnv.sh` compares
`pythia8-config --version` against `HF_PYTHIA8_VERSION` and `root-config
--version` against `HF_ROOT_VERSION`, and exports nothing on a mismatch. A
CVMFS package path used to encode its own version; a locally built prefix does
not, so a rebuild in place could otherwise change the generator while every
recorded string stayed byte-identical.

---

## Machine-specific paths

These are the only values that differ between machines. All are set in
`config/dependencies.local.conf`; the tracked defaults in
`config/dependencies.conf` describe the Nikhef installation.

| Variable | Nikhef default | What it is |
|---|---|---|
| `HF_PYTHIA8_PREFIX` | `/data/alice/ipardoza/pythia_stock_8317/install` | **A personal directory.** The single biggest portability weakness: the tarball checksum is recorded but nothing rebuilds it automatically. A third party cannot reproduce the environment without building PYTHIA themselves. |
| `HF_PYTHIA8_GCC_PREFIX` | `/cvmfs/.../GCC-Toolchain/v14.2.0-alice2-2` | Compiler runtime the PYTHIA build and producer link against. |
| `HF_ROOT_PREFIX` | `/cvmfs/.../ROOT/v6-30-01-alice5-2` | CVMFS-only. Absent off-cluster. |
| `HF_ROOT_GCC_PREFIX` | `/cvmfs/.../GCC-Toolchain/v12.2.0-alice1-9` | Compiler runtime ROOT needs. |
| `HF_ROOT_ALIENV_PACKAGE` | `VO_ALICE@ROOT::v6-30-01-alice5-2` | Set empty to skip alienv and use `HF_ROOT_PREFIX` directly. |
| `HF_ROOT_RUNTIME_LIB_DIRS` | eleven `/cvmfs/...` library directories | Used only when alienv cannot initialise. |
| `HF_PRODUCTION_ROOT` | `<checkout>/Production` | **Set this on any machine that runs jobs.** Where raw output is written. |

Resolution order, enforced by every entry using `: "${NAME:=default}"`:

```
exported environment variable
  > config/dependencies.local.conf   (untracked, machine-specific)
    > config/dependencies.conf       (tracked defaults)
```

`HADRONIZATION_DEPENDENCIES_CONF` replaces the tracked file wholesale.

### Two more paths, resolved rather than configured

- **`HADRONIZATION_BASE`** — the checkout root. Resolved as: exported value,
  then `base_path.txt` (untracked) if present, then the directory containing
  `setupEnv.sh`. You normally never set it. `runCondorJob.sh` **refuses** to
  inherit it, along with every other campaign-control variable, so a
  resubmission cannot silently run under settings no submit file recorded.
- **`HF_PRODUCTION_ROOT`** — data root, deliberately separate from the code
  checkout. Raw output for four tunes at 100M events each is roughly 360 GB.

---

## Storage

Approximately **0.9 GB per million events**, so:

| Campaign | Events | Raw output |
|---|---|---|
| Preliminary, 4 tunes x 50 jobs x 100k | 20M | ~18 GB |
| Full, 4 tunes x 1000 jobs x 100k | 400M | ~360 GB |

`make doctor` reports free space at the production root and warns below 400 GiB.

Nikhef's `/data/alice` was last observed at 96% used with 1.6 TB free. A full
four-tune campaign fits, but not with much room. Confirm before submitting.

---

## This checkout is a git worktree, not a clone

**Verified 2026-08-08 by reading the `.git` entry**, which is a *file*, not a
directory:

```
gitdir: /Users/wax/Documents/Research/Projects/Hadronization/.git/worktrees/Hadronization-full-production
```

So `Hadronization-physics-focus/` is a **linked worktree** of
`Hadronization/`. There is **one repository and one object store**; the two
directories are two checked-out refs of it, not two copies.

**Note the name mismatch:** the worktree's internal gitdir is
`Hadronization-full-production` while the directory is
`Hadronization-physics-focus`. The directory was renamed after the worktree was
created — harmless, since git tracks the link by path, but it means **grepping
for the directory name will not find the worktree's metadata.**

**Practical consequences:**

- **`git worktree list` from either directory shows both.** The sibling
  `Hadronization/` is `main`; this one is `physics-focus`. If `Makefile`,
  `tools/`, `docs/` or `RELEASE_BLOCKERS.md` appear to be missing, **you are in
  the wrong directory, not looking at a broken repository.**
- **A commit made here is immediately visible there** — same object store, no
  fetch, no push.
- **Git refuses to check out the same branch in two worktrees.** That refusal
  is a safety net, not an obstacle.
- **Deleting either directory does not delete the repository** — but deleting
  `Hadronization/` takes the shared `.git` with it and orphans this worktree.

### What this means for B8

**B8 asks which tree the paper's reproducibility statement should resolve to.**
The worktree fact narrows it usefully: **`main` and `physics-focus` are two refs
in one repository, not two repositories.** The options B8 lists — merge
`physics-focus` into `main`, replace `main` with it, or publish from
`physics-focus` — are therefore all **ref operations inside a single object
store**, with no cross-repository synchronisation and no risk that one history
is unreachable from the other. Any clone carries both.

**This does not decide B8.** Which ref a reader lands on when they follow a URL
is still an owner decision, and still must not be left until submission. It only
removes one class of difficulty from every option.

---

## The bibliography is authoritative in Overleaf, not here

`Literature/References.bib` is a **working artifact**. The authoritative
bibliography for the manuscript lives in Overleaf, and that is where entries are
added, corrected and cited from. The copy in this repository exists so the
sources travel with the code and so a reader can see what the analysis cites; it
is not the file the paper is built from.

**What follows from that.** A difference between this file and Overleaf is not a
defect to be reconciled by a script, and no pipeline step reads it. When the two
disagree, Overleaf wins. Treat a change here as a convenience copy, and make the
real edit upstream.

---

## Known non-portable leftovers

Three legacy scripts contain hardcoded paths under `/data/alice/pveen/...`,
a *different user's* directory:

- `Balancing_and_Sampling/GenerateOutputs.sh`
- `Balancing_and_Sampling/CalculateErrors/GenerateOutputs.sh`
- `SimulationScripts/Batching_MONASH.sh`

They are not part of the production, analysis, or plotting pipeline and nothing
in the current chain calls them. They are left untouched rather than
half-fixed; treat them as historical.

---

## What runs where

| Task | Anywhere | Needs ROOT+PYTHIA | Needs Condor |
|---|---|---|---|
| `make doctor`, `make cards`, `make registry` | yes | | |
| `make submit-prelim`, `make submit-full` | yes | | |
| `make test` | partly -- see below | 5 of 21 | |
| `make build` | | yes | |
| `Validation/*.C`, analysis, plotting | | yes | |
| `condor_submit`, `condor_q`, `condor_rm` | | | yes -- **`stbc` only** |

### `make test` and ROOT

Sixteen of the 21 contract tests are standard-library only. **Five compile or
run a ROOT macro and FAIL rather than skip when ROOT is absent.** They are
`test_analysis_boundary_binning`, `test_analysis_raw_input_contract`,
`test_pair_block_closure`, `test_pair_trigger_identity`,
`test_plot_dataset_integration`.

`tools/run_tests.sh` sources `setupEnv.sh` itself, so `make test` and
`make check` are correct on the cluster with no prologue. It prints the
resolved `root` path first, or a warning that a run without ROOT **is not a
green run**. Read that line before believing the count.

**The C++ standard is taken from `root-config`, never hardcoded.** This
matters more than it looks: a laptop's ROOT and the cluster's are not the same
build.

| | version | `root-config --cflags` |
|---|---|---|
| laptop (homebrew) | 6.38.04 | `-std=c++17` |
| Nikhef (CVMFS, pinned) | 6.30.01 | `-std=c++20` |

`tests/test_validate_raw_output_strict_compile.py` used to pin `-std=c++17`
and strip ROOT's own flag. That silently matched the laptop and mismatched the
cluster, where `RConfigure.h` emits a standard-mismatch `#warning` that
`-Werror` turns into an error -- so the test failed on a ROOT header rather
than on the macro under test. It now uses whatever standard ROOT reports.
All six warning flags (`-Wall -Wextra -Wpedantic -Wconversion -Wshadow
-Werror`) are unchanged.

Note the producer is genuinely C++20 on the cluster regardless of
`generation/producer/Makefile:51` asking for `-std=c++17`: ROOT's `--cflags`
appends `-std=c++20` after it and GCC honours the last flag.

The Python contract tests are standard library only and run on any machine,
including macOS with no ROOT. That is deliberate: it keeps the parts of the
pipeline that can be checked cheaply checkable everywhere.

**Nikhef remains authoritative** — it is the only place the producer compiles
and the only place a physics number can be produced.

### Getting there

```bash
ssh -o BatchMode=yes nikhef
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc
```

`stbc` sets `RemoteCommand` in ssh config; without those two overrides the
command hangs.

Two further site quirks worth knowing:

- Git sync is by bundle. Nikhef cannot reach GitHub.
- A detached process on `/data/alice` loses the autofs mount when its SSH
  session ends **if it opens new files**. Long builds must run synchronously;
  long runs survive as long as they only write to already-open descriptors.

> **This quirk has now cost a measurement.** The v3 scaling series ran detached
> on the login node; its 50-input point opens 300 new pair files and needs about
> half an hour, and it died with the session at 69 files. The 10- and 25-input
> points survived only because they finished in 45 s and 135 s. **Anything that
> writes many files and runs for minutes belongs on a batch node**, whose
> lifetime is the schedd's business rather than an SSH session's.

---

## The checkout-freeze hook on Nikhef

`tools/install_checkout_guard_hook.sh` installs a `reference-transaction` git
hook into a clone that runs jobs. **Installed on
`/data/alice/ipardoza/Hadronization` on 2026-08-09.**

```bash
tools/install_checkout_guard_hook.sh --repo /data/alice/ipardoza/Hadronization --print   # dry run
tools/install_checkout_guard_hook.sh --repo /data/alice/ipardoza/Hadronization           # install
```

**Why a hook and not `make can-advance`.** The Makefile guard only helps the
person who remembers to run it; raw `git checkout`, `reset`, `merge` and `pull`
bypass it. Worse — and this was not known when the hook was first proposed —
**the guard does not exist on Nikhef at all.** The checkout is detached at
`61fe978f`, and the guard was committed later at `7e1f7e7`, so `make can-advance`
there answers `No rule to make target 'can-advance'`. Restoring the pin, the
correct remedy for the freeze breach, also uninstalled the mechanism built to
prevent it.

`.git/hooks/` is not part of the working tree, so the hook survives checkout
moves. It is **self-contained** — it re-implements the two-condition probe
rather than importing `tools/queue_probe.py`, which the pinned tree does not
have.

**`reference-transaction` is the only hook that can hold the invariant.**
`post-checkout` runs after the move and can only warn; `pre-merge-commit` does
not fire for a fast-forward, which is exactly how a pin gets advanced.

- Fires only on updates that move **HEAD** or the branch HEAD points at.
  `git fetch` writing `refs/remotes/*` is not blocked — verified.
- **Fail-closed.** On the **login node `condor_q` is not installed**, so the
  probe returns UNKNOWN and the move is refused. That is correct: a host that
  cannot ask whether jobs are in flight should not be moving a pinned checkout.
  **Move the checkout from `stbc`.**
- Override records a reason, echoed and appended to `.git/checkout_guard.log`,
  and logs `OVERRIDE` distinctly from `ALLOWED`:

```bash
HADRONIZATION_CHECKOUT_OVERRIDE_REASON="restoring the pin to <sha>" git checkout <sha>
```

> ### THE LESSON, ratified 2026-08-09 — why this shape, not just this hook
>
> **A safety mechanism must live outside the object it guards.**
>
> `make can-advance` was version-controlled *inside the tree whose version it
> controlled*. So the one action it most needed to survive — detaching to an
> older commit to restore a pin — **deleted it**, precisely when it was most
> needed. The guard was correct, tested, and absent.
>
> The hook works because `.git/hooks/` is **not** the guarded object: moving the
> checkout cannot touch it. Its self-containment is the same principle applied
> once more — importing `tools/queue_probe.py` would have reintroduced the
> dependency on the tree that the detach removes.
>
> **Generalise before assuming this is only about git.** Any check whose
> lifetime is coupled to the state it validates has this failure mode. A
> validator shipped inside the dataset it validates, a lint rule stored in the
> branch it lints, a monitor deployed by the pipeline it monitors — all fail
> silently and exactly when the guarded thing moves.

**Verified live, both directions.** Real `git checkout` refused with
`fatal: ref updates aborted by hook` (exit 128, HEAD unchanged) and then
succeeded under a recorded override — exercised in a **throwaway `--local`
clone**, so that proving the abort never risked the pinned repository. On the
pinned repo itself the installed hook (byte-identical, verified by sha256) was
driven through its real interface in both directions: refuse `exit 1` on
`UNKNOWN` (login) and on `NONEMPTY` (`stbc`, 2221 jobs), allow `exit 0` under a
recorded reason. **A HEAD-moving `git` command was deliberately never run
against the pinned repo** — testing a safety device is not worth gambling the
campaign it protects.
