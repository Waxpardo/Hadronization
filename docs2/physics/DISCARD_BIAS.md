DRAFT — UNRATIFIED. Requires the owner's and the supervisor's sign-off before any use in the manuscript.

# Can the discarded jobs bias the measured observable?

Drafted by session WRAP over artifacts that already exist. Session PHYS-1
checked every citation, corrected three arguments, and added four things the
first draft did not carry: the generator-version gap, the three artifacts in
this repository that limit the mechanism claim, the guard design that bears on
the wedge-versus-slow question, and an arithmetic check against the pilot's own
hang rate. No number here is a new measurement. Each is derived from a cited
artifact.

The question a referee will ask is short: *you discarded about six percent of
your attempts in the two tunes where you claim an effect — how do you know the
effect is not an artefact of what you discarded?*

**Read §3 and §4 before using this page.** §3 states what the artifacts cannot
show. §4 states that the mechanism was measured on a different generator
version from the one that produced the paper.

## 1. The measured attrition

Recorded per tune in `config/cr_holdout_policy_v1.json`, `observations`
(`:6-9`), and tabulated in
[../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) `:82-87`:

| tune | discarded attempts | total attempts | rate |
|---|---:|---:|---:|
| MONASH | 0 | 1,000 | 0.00 % |
| JUNCTIONS | 63 | 1,063 | 5.93 % |
| CLOSEPACKING | 64 | 1,064 | 6.02 % |
| **all three** | **127** | **3,127** | **4.06 %** |

The 127 and the 4.06 % are sums over the three recorded rows. The file states
the rows, not the totals. Across the two junction tunes alone the rate is
127 / 2,127 = **5.97 %**.

The attrition is entirely in the two junction tunes. That is what makes the
question sharp: it is not uniform noise. It is concentrated in exactly the
configurations under study. The decision to accept it is recorded as
`accepted_by_supervisors` (`config/cr_holdout_policy_v1.json:3`) and ruled in
R41.

## 2. The mechanism, as the pilot study recorded it

`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:13-15` records
the state directly. Four of nine pilot jobs "entered an **unbounded rejection
loop inside PYTHIA** and will never terminate. They are not slow — they are
wedged." Identical stack traces in all four put the loop at
`Pythia8::JunctionSplitting::splitJunGluons`, reached through `checkColours`
from `PartonLevel::next` (`:58-74`).

Why it cannot terminate is read from source at `:182-209`. `StringZ::zLund`
samples `z` by accept–reject with no iteration cap, and for the degenerate
junction-leg kinematics that `splitJunGluons` hands it, the acceptance
probability collapses to approximately zero. The caller's own retry loop is
likewise uncapped. One sample showed `__math_invalid` beneath `pow`, and the
study notes that a NaN `z` fails every comparison, so the loop "is provably
non-terminating once that state is reached, not merely slow" (`:84-86`).

Why only two tunes reach it is a tune setting, not a fault (`:107-111`). The
junction tunes set `ColourReconnection:allowDoubleJunRem = off`, which removes
the cheap path for dissolving a connected double-junction system and forces the
split. The record states that this "is a deliberate physics setting from the
QCD-CR tune, **not** a configuration error." MONASH sets none of the three
implicated settings and hung 0 of 3. The two junction tunes hung 4 of 6
(`:104-105`).

The sentence this page is sometimes asked to carry is at `:215-218`, inside the
section that argues for a source patch:

> **Consequence for the fix: there is no correct event waiting at the end of
> the loop.** PYTHIA cannot generate these events. No fix can include them, so
> "unbiased" can only mean *lose as few as possible, and make the loss exactly
> countable* — not *lose none*.

Read in full it is a statement about the loop: once `splitJunGluons` reaches the
degenerate kinematics, no event emerges from that path. §9 states what it does
**not** license.

## 3. What this repository cannot show

Three artifacts limit the mechanism claim. A page that omits them will not
survive a referee who finds them.

**The wedge-versus-slow gap.** The policy's language is "A failed **or
guard-terminated** attempt promotes no ROOT file"
(`config/cr_holdout_policy_v1.json:11`). That covers two different things: a job
wedged in `splitJunGluons`, and a job the guard terminated for another reason.
`docs/REPRODUCIBILITY.md:147` says the record that would separate them is
absent:

> The external ledger and attempt metadata are absent. This checkout cannot
> independently derive those discard counts or rates.

**The mechanism is recorded as unestablished.** Two further sentences in the
same file say so. `docs/REPRODUCIBILITY.md:135`: "A repeat with one recorded
seed and card did not reproduce its wedge." And `:137`: "The retained pilot
inputs cannot establish the wedge mechanism. The final campaign record also
leaves event-content correlation unmeasured." `docs/GOLDEN_OUTPUTS.md:1066` row
N4 records the same reproduction attempt and its consequence in that document's
own words: "identical inputs, different behaviour; mechanism unexplained".

So this repository holds both a source-level account of why the loop cannot
terminate and a record that the wedge did not reproduce under identical inputs.
Both are true, of different things. The non-termination is a property of the
loop once its degenerate state is reached. The reachability of that state from a
given card and seed did not reproduce. **Nothing in this repository explains the
second**, and the mechanism claim must say so.

**What the artifacts do and do not support.** They support "127 attempts were
discarded, and the campaign record attributes the mechanism to the junction
hang". They do **not** support "each of the 127 was individually confirmed to be
wedged in `splitJunGluons`". The pilot traced four jobs directly. The production
attribution is by rate and by tune, not per attempt.

## 4. The generator-version gap

The pilot study measured PYTHIA **8.315**
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:6`). The
campaign that produced the paper ran PYTHIA **8.317**, from the unmodified
official tarball (`docs/REPRODUCIBILITY.md:27`, `:29`; `docs/GOLDEN_OUTPUTS.md`
row C-1 at `:1002`). Every stack trace, the hang rate used in §6, and the
"PYTHIA cannot generate these events" sentence are 8.315 measurements.

Two consequences, and they point in opposite directions.

**The bug is expected to persist.** The study checked upstream through 8.317 and
found no fix: "Neither 8.316 nor 8.317 contains any fix to `splitJunGluons` or
`zLund`"
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:174`). That is a
check of the upstream changelog, not a measurement on 8.317. It is also the
reason the qualitative mechanism carries across the version boundary.

**The rate need not carry.** 8.316 changed trial-hadron generation in the
close-packing framework, and the study calls that "a physics-correctness issue
independent of the hang and … arguably more serious than the hang itself"
(`:266-269`). 8.316 also added `StringFragmentation:eJunctionCutoff` and
`mJunctionCutoff`, which the same study says "may bear on the degenerate
kinematics feeding the loop" (`:271-273`). CLOSEPACKING is one of the two
affected tunes. The 8.315 hang rate is therefore an estimate for a generator the
campaign did not run.

**The recommended patch was not applied.** The study's §5.3 recommends patching
`zLund` with a bounded retry so the event aborts through PYTHIA's own channel.
The runtime contract records an unmodified 8.317 tarball with a recorded SHA-256
(`docs/REPRODUCIBILITY.md:29`), so that patch is not in the production
generator. Wedged jobs therefore still wedge, and the guard is what removes
them. That is the premise §5 and §7 rest on, and it is measured rather than
assumed.

## 5. What the campaign's design says about wedge versus slow

The per-attempt record is absent (§3). The design is not, and it bears on the
question.

**The guard is on CPU time, not wall clock.**
`generation/submit/Condor_README.md:115-122` gives the reason: "A wedged job
burns CPU continuously (the four historical hangs ran at CPU/wall = 0.97); a
healthy job on a contended node does not". A busy worker node accumulates wall
time, not CPU time, so contention cannot trip the CPU arm. The threshold is
3,600 CPU seconds, "about 4.7x the slowest normal job (CLOSEPACKING, 762s)"
(`:124`); 3600 / 762 = 4.72. For a healthy job to trip that arm it must consume
almost five times the CPU of the slowest normal job.

**The wall arm is the residual hole.** The same expression also holds a job
after 14,400 wall seconds (`generation/submit/Condor_README.md:106-107`,
rendered by `tools/render_production_submit.py:334-337`). A healthy 762-second
job trips it at CPU/wall = 762 / 14400 = 0.053. That is far below the 0.33 the
runbook cites for a contended node (`generation/submit/Condor_README.md:117`),
but it is not impossible, and the wall arm is the one path by which a healthy
job can join the 127.

**The hold reason cannot tell the two arms apart.**
`tools/render_production_submit.py:338-342` renders one static string for both:
`"HF_HANG_GUARD suspected generator hang: cpu>3600s or wall>14400s"`. The retry
path reads only that string. `tools/resubmit_held.py:55` queries `HoldReason`,
and `:271-274` splits held jobs on whether the marker is present. No tool in
this repository reads `RemoteUserCpu` back; it appears only in the submit
expression that writes it and in the test that pins it
(`tests/test_submit_rendering.py:114`). This changes what "recover the ledger"
would mean, and §8 states how.

## 6. An arithmetic check the campaign permits

The pilot measured 4 hangs in about 3.63 million junction-tune events, "≈ 1.1
hangs per million events"
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:130-131`).
Production jobs generate 100,000 successful events each
(`docs/REPRODUCIBILITY.md:133`).

If every discard were a hang at the pilot's rate, the expected share of attempts
lost would be 1 − exp(−1.102 × 10⁻⁶ × 10⁵) = **10.4 %**, about 222 of the 2,127
junction-tune attempts. The study made the same forecast on its own numbers and
in event terms: "with ~200 M events in junction tunes, expect **~220 hangs**"
(`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:139-140`). The
observed figure is 127, **5.97 %**, which implies a per-event rate of
−ln(1 − 0.0597) / 10⁵ = 6.2 × 10⁻⁷, about 0.62 per million.

The exact Poisson 95 % interval on 4 counts is [1.09, 10.24], so the pilot rate
is 0.30 to 2.82 per million events. The implied production rate, 0.62, sits
inside it.

**What this does and does not establish.** The observed attrition is fully
accounted for by the hang rate alone, and it sits *below* the pilot's central
prediction. The observation therefore requires no population of healthy jobs
killed for slowness. It does not exclude one: a lower true hang rate plus a small
slow contingent fits equally well. The check also crosses the version boundary of
§4 and rests on four counted events. Treat it as consistency, not as
measurement.

## 7. The bound

The promoted sample is conditioned on completion, and completion requires that
no event in the block triggered the hang.
[../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) `:98` states the
conditioning in those terms: "Completed files are conditioned only on **zero
hang-triggering events**." The promotion path reads no other property of the
events. `config/cr_holdout_policy_v1.json`, `handling`, conditions on a failed
attempt promoting nothing (`:11`), regeneration under a new deterministic seed
(`:12`), and manifest membership (`:13`). It names no property of the generated
events. The manifest builder reinforces it: `docs/REPRODUCIBILITY.md:143`
records that it "orders promoted logical identifiers before assigning canonical
slots. It never selects the first jobs to finish."

So the systematically absent population is not the discarded jobs' ordinary
events. Those were an unbiased draw, replaced by an equivalent draw under a new
seed. It is the **hang-triggering events themselves**, and they are countable: a
job wedges on the first one it meets and generates nothing after it, so each
discarded attempt corresponds to exactly one such event.

Inputs, each cited:

- delivered sample: 1,000 canonical slots per tune × 100,000 successful events
  per job × 3 tunes = **3 × 10⁸ events** (`docs/REPRODUCIBILITY.md:133`;
  [../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) `:72`);
- discarded attempts: **127** (`config/cr_holdout_policy_v1.json:6-9`, summed);
- hang-triggering events per discarded attempt: **at most one**, because the job
  never proceeds past the event it wedged on
  (`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:13-15`).

The arithmetic: 127 / (3 × 10⁸) = **4.2 × 10⁻⁷**, about one event in 2.4
million.

Two corrections, both small, both stated rather than folded in. An unbiased
sample of the same size would contain blocks holding more than one
hang-triggering event; at the rate implied in §6 that is 3.0 % of affected
blocks, so the count above understates the absent population by about that much.
And if some of the 127 were healthy jobs killed by the wall arm of §5, the count
overstates it, because such a job contributes no systematically absent event at
all. **The bound is an upper bound under either reading of the gap in §3.**

Against an attempt attrition of 4.06 %, the two figures differ by five orders of
magnitude because they count different things. The percentage counts **jobs**.
The bound counts **events**.

## 8. What would close the gap, and what it would cost

The first draft of this page said the gap needs "the external attempt ledger —
per attempt, its termination cause and its exit path". §5 shows that is not
sufficient, and naming the wrong evidence would send someone to recover a record
that cannot answer the question.

**The discriminating quantity is `RemoteUserCpu` per held attempt**, not the
hold reason. The hold reason is one static string for both guard arms. A ledger
that carries the termination cause in the form the pipeline wrote it will show
`HF_HANG_GUARD` for all 127 and separate nothing.

Three routes, in increasing cost:

1. **The submit host's Condor history.** `RemoteUserCpu` and `CommittedTime` per
   held job give the CPU/wall ratio directly, and the 0.97-versus-0.33
   separation of `generation/submit/Condor_README.md:116-118` is then decisive
   per attempt. Cost: one query, if the history has not aged out. This
   repository cannot tell whether it survives.
2. **The partial files on the data plane.** A killed attempt leaves a partial
   ROOT file with no sidecar, which is how `tools/campaign_status.py:81-84`
   counts discards at all. The pilot estimated events-before-hang from partial
   size against a per-event byte rate
   (`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:113-128`). A
   job wedged early carries a small partial; a healthy job killed near
   completion carries a nearly full one. Cost: a directory listing and one
   division, **if** the partial area under `/data/alice/ipardoza` still holds
   the 127 files. That path is not reachable from this checkout.
3. **A bounded re-run.** Regenerate the discarded logical slots under their
   recorded seeds, with the guard instrumented to record which arm fired. Cost:
   127 jobs. `docs/REPRODUCIBILITY.md:302` records 562.5 CPU-hours for the full
   3,000-job generation, so 127 jobs is of order 24 CPU-hours. The caveat is N4
   in §3: a re-run under a recorded seed has already once failed to reproduce a
   wedge.

Route 2 is the cheapest route this project can still act on, and it needs no
cluster time. **This session ran none of the three.**

## 9. What the paper may assert

Stated plainly, because a page that argues one thing and is read as arguing more
is worse than no page.

**Supported.** That 127 of 3,127 attempts were discarded, 4.06 %, none in
MONASH. That the campaign record attributes the mechanism to an unbounded
accept–reject loop in PYTHIA's `splitJunGluons`, reached under the junction
tunes' `allowDoubleJunRem = off`. That promotion is conditioned on completion
and manifest membership and reads no property of the generated events. That on
the campaign's own conditioning, the population of events absent for a reason
correlated with the physics is bounded above at order 10⁻⁶ of the delivered
sample, with the assumptions of §7 stated.

**Not supported.** That every discard was individually confirmed to be a wedge
(§3). That the hang reproduces from a recorded card and seed — the one recorded
attempt did not (§3). That the 8.315 hang rate is the rate of the 8.317 campaign
(§4). That any bias was *measured*: this page bounds the population that could
carry one. No variation of the observable under a discard model was computed,
and `docs/REPRODUCIBILITY.md:137` records event-content correlation as
unmeasured.

**Out of scope.** Systematic uncertainties, which are paused under ruling R31
and are treated in [../paper/LIMITATIONS.md](../paper/LIMITATIONS.md).

## 10. Recommended framing, for the owner and the supervisor

*A recommendation, and labelled as one.*

The manuscript should state this as a **limitation of the generator**, not as a
defensive disclosure about discarded jobs — and it should not state it as
strongly as the pilot study's sentence alone would allow. What the source
analysis establishes is that PYTHIA 8.315's `zLund` accept–reject cannot
terminate once `splitJunGluons` reaches degenerate junction-leg kinematics, so
no event ever emerges from that path, and the upstream changelog check says
8.317 carries the same code. On that reading the hang-triggering configurations
lie outside the generator's reachable output at these settings, campaign or no
campaign, and the discarded jobs are the symptom rather than the cause. That is
why the honest sentence is about PYTHIA and not about job attrition. Against
that, this repository records that the wedge did not reproduce under a recorded
card and seed, and calls the mechanism unexplained (`docs/GOLDEN_OUTPUTS.md:1066`;
`docs/REPRODUCIBILITY.md:135`, `:137`), and the rate was measured on a version
the campaign did not run (§4). The recommendation is therefore to write the
generator limitation as the substance, and to disclose the reproduction failure
and the version gap in the same breath, so that a referee who finds N4 finds it
already declared. A disclosure that concedes its own weakest point is stronger
than one a referee has to discover.

## 11. Status

This page is **unratified**. No owner and no supervisor has signed it. Ruling
R41 accepts and discloses the hang rates; it does not accept this argument,
which did not exist when R41 was made. R41 also records that the architect's
completed-file conditioning bound is available if the owner wants the disclosure
to read "bounded, negligible" rather than "unmeasured", and that the wording is
the owner's editorial call in Overleaf under ruling R38. §7 is that bound,
written out with its assumptions.
