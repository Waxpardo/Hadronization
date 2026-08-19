# Merge supervisor built; the preamble skip is written but NOT deployable — 2026-08-14 (sixteenth session)

**Suite 44/44.** Wall clock 14:22–14:45 CEST. `stbc-i3` up **39 h 15 m**, boot
2026-08-12 23:07 — no reboot.

> **Headline: Task 1 succeeded, Task 2 is committed but could not be deployed,
> and Task 3's restart went onto the UNMODIFIED driver. I stopped the merge
> before establishing that the fix was deployable, and it was not. That cost
> roughly 6 hours.** The full accounting is in §4.

---

## 1. Task 1 — the supervisor. DONE.

`tools/merge_supervisor.sh`, running as **PID 316182**, poll 120 s.

It polls for the merge, and on death re-runs every pre-check a human ran by
hand yesterday: tracked-clean, HEAD pinned, **reflog unmoved** (the check that
HEAD was not moved and moved back), canonical manifest sha, and CVMFS python3
**executed rather than stat'ed** — the symlink survived the outage that killed
v4; only its target vanished, so `-e` would have returned a false pass. All
pass → restart with the identical command. Any fail → log and **stop**.

> A supervisor that restarted blindly would have relaunched into a missing
> interpreter every 60 seconds all night and buried the real cause under
> thousands of identical failures. Fail-closed is the whole design.

**Verified before launch, and this mattered:** `merge_pid()`'s pattern was
tested against the live merge first. Had it failed to match, the supervisor
would have concluded the merge was dead and started a **second** one. It
matched exactly one PID. With the merge alive, the log shows `SUPERVISOR
observed merge pid=…` and **no restart attempted** — the required negative
control.

**Two self-match traps hit while doing this**, both the same shape: `pgrep -f
<pattern>` and `pkill -f <pattern>` match *my own shell*, whose command line
contains the pattern text. The `pkill` one killed my session mid-script and
silently skipped the rest of it. **Neither the supervisor nor any check should
count processes with a pattern that appears in the counting command.** Use
explicit PIDs, or `ps` + a bracketed grep, and verify the count independently.

## 2. Task 2 — the fix is written, tested, committed (`c3c9d96`) — and NOT deployed

Both halves are in the repo and the suite passes:

**The skip.** `merge_root_files.sh` now reads the existing
`analysis_output_manifest_validation.json` and reuses it when it is a PASS over
**the same manifest sha**, logging `ANALYSIS_OUTPUT_MANIFEST_SKIPPED` with the
report's sha and timestamp. Verified against the live report, with negative
controls for a wrong manifest sha and a wrong row count — both correctly refuse.
Reuse is corroborated rather than assumed: **v4 independently re-validated the
whole set on Aug 13 and reached the same PASS.**

> **Content-neutrality.** It is a PRECONDITION CHECK, not a transformation: it
> reads inputs and writes one report, and no merged byte depends on whether it
> ran. The merged content is produced by `MergeCanonicalAnalysis.C` and
> `MergeAnalysisObjects.C` — untouched by this commit, and pinned *by sha at the
> recorded commit* by `merged_pair_provenance.py`. Every promoted directory is
> still validated twice on its own path before the `mv`.

**The misleading error.** Exit 126/127 now reports **ENVIRONMENT** and states
that nothing was validated and nothing is known to be wrong with the directory;
a genuine non-zero verdict reports **DATA** and states that both checks ran.
*"We could not look" is never evidence of "we looked and it was bad."*

### Why it is not deployed — three independent blockers

1. **`git archive` to scratch is technically impossible here.**
   `merged_pair_provenance.py` validates every existing promoted directory with
   `git merge-base --is-ancestor` and `git show <merge_commit>:<file>`. An
   archived tree has no `.git`, so the merge would fail on the first
   already-promoted directory. The standing A2 deploy rule does not transfer to
   the merge driver.
2. **The Nikhef checkout is 123 commits / 473 files / +84 731 lines behind.**
   It sits at `43e35be8`, which **predates the restructure** — its driver is
   `merge_root_files.sh` at the repo root, not `merging/merge_root_files.sh`.
   Advancing it to `c3c9d96` would apply the entire restructure to the live
   production merge path. That is not a targeted deployment.
3. **A deliberate pin guards exactly this**, and its hook says in terms: *"Do
   NOT delete the pinfile to get past this message."* The pin names a detached
   run — which is precisely what the merge is, and what the Condor-queue probe
   cannot see. I did not remove it.

**And the minimal backport is not trivial either:** the deployed driver
(`75708821…`) and the repo's pre-edit driver (`a6fe8a34…`) have **diverged**, so
the patch does not apply cleanly. Backporting means writing a *different*,
unreviewed patch directly onto the production merge path.

**Owner decision needed.** The options are (a) backport a minimal, separately
reviewed driver patch onto `43e35be8`, (b) advance Nikhef across the restructure
as its own supervised operation, or (c) leave it: the supervisor already cuts
detection latency from 10.6 h to ~2 min, which was the larger half of yesterday's
loss.

## 3. Task 3 — which path, and why it changed

Measured properly, from the **worker**, not the parent: the preamble was at
`per_job/JUNCTIONS/slot_167` → **row 1168 of 3000 in manifest order**, advancing
at **13.9 s/directory** (39 directories over 541 s). **≈ 6.9 h remaining** —
comfortably over the 4 h threshold, so the brief's ruling was *restart onto the
fixed driver*.

> An instrument note: `rchar` was **363 GB against a 285 GB** total for the raw
> loop, i.e. **127 %**. The read model was therefore not validated and the
> fraction was meaningless — but it did establish that the raw loop had finished
> and the per-directory phase had begun. The usable position came from the
> worker's actual argument (`slot_167`) resolved against manifest order, per
> `PROGRESS_PROBE_METHOD.md` §3.

I stopped the merge, then discovered the fix was not deployable. **The restart
therefore went onto the unmodified `43e35be8` driver** (sha re-verified
`75708821…` before launch). Merge is **PID 315689**, exactly one instance,
supervisor attached.

## 4. The cost, stated plainly

Stopping the merge discarded **≈ 5.5 h of completed preamble** (row 1211 of
3000), and the restart begins that 12 h 42 m phase again from zero.

**I checked the guard, the provenance requirements and the ancestry rule before
stopping the merge. I did not check that the deployed checkout was 123 commits
behind — and that was the fact that decided it.** The cheap check was the one I
skipped, and it was cheap: one `git rev-list --count`.

> **The rule this earns: establish that a fix can be deployed to the target
> BEFORE stopping the thing it is meant to improve.** Deployability is a
> property of the target, not of the patch, and it is knowable in one command.

Nothing was lost or corrupted. No partial was touched, nothing was promoted or
deleted, and the frozen checkout ends the session exactly as it began —
`43e35be8`, tracked-clean, pin intact, driver sha unchanged. The aborted
fast-forward left the checkout dirty for a few minutes; `git reset --hard` back
to `43e35be8` reverted my own operation, and the new commit is retained as
`refs/remotes/bundle/physics-focus`, so no history was lost.

## 5. Revised estimate for JUNCTIONS 10/10

From the 14:42 restart: **preamble 12 h 42 m** → ~03:25 Aug 15; **15
re-validations** of the already-promoted directories (MONASH central + 10,
JUNCTIONS central + 3) at ~15 min → ~07:10; **7 fresh JUNCTIONS block merges** at
~45 min → **≈ midday Aug 15**.

Had the merge been left alone, ~06:30 Aug 15. **The delta is the ~6 h in §4.**

## Next session

1. The owner decision in §2 on deploying the skip.
2. JUNCTIONS harvest when it reaches 10/10 — not before.
