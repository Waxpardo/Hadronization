DRAFT — UNRATIFIED. Requires the owner's and the supervisor's sign-off before any use in the manuscript.

# Can the discarded jobs bias the measured observable?

Drafted by session WRAP as a documentation act over artifacts that already
exist. It introduces no number that is not already recorded. Session PHYS-1
ratifies it, or does not.

The question a referee will ask is short: *you discarded about six percent of
your attempts in the two tunes where you claim an effect — how do you know the
effect is not an artefact of what you discarded?* The repository's own
mechanism answers it, and the answer has been written nowhere until now.

**Section 3 states one thing the artifacts in this checkout cannot show.** Read
it before using this page.

## 1. The measured attrition

Recorded per tune in `config/cr_holdout_policy_v1.json`, `observations`
(`:5-9`), and tabulated in
[../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) `:82-87`:

| tune | discarded attempts | total attempts | rate |
|---|---:|---:|---:|
| MONASH | 0 | 1,000 | 0.00 % |
| JUNCTIONS | 63 | 1,063 | 5.93 % |
| CLOSEPACKING | 64 | 1,064 | 6.02 % |
| **all three** | **127** | **3,127** | **4.06 %** |

The attrition is entirely in the two junction tunes. That is the fact that
makes the question sharp: it is not uniform noise, it is concentrated in
exactly the configurations under study. The decision to accept it is recorded
as `accepted_by_supervisors` (`:3`).

## 2. The mechanism

Every hang is one failure, in one function, on one event.

`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:13-15` records
the state directly: four of nine pilot jobs "entered an **unbounded rejection
loop inside PYTHIA** and will never terminate. They are not slow — they are
wedged." Identical stack traces in all four put the loop at
`Pythia8::JunctionSplitting::splitJunGluons`, reached through
`checkColours` from `PartonLevel::next` (`:58-74`).

Why it cannot terminate is read from the source at `:180-213`:
`StringZ::zLund` samples `z` by accept–reject with no iteration cap, and for
the degenerate junction-leg kinematics `splitJunGluons` hands it, the
acceptance probability collapses to approximately zero. The caller's own retry
loop is likewise uncapped.

Why only two tunes reach it is a tune setting, not a fault
(`:107-111`): the junction tunes set
`ColourReconnection:allowDoubleJunRem = off`, which removes the cheap path for
dissolving a connected double-junction system and forces the split. The record
states plainly that this "is a deliberate physics setting from the QCD-CR tune,
**not** a configuration error." MONASH sets none of the three implicated
settings and hung 0 of 3; the two junction tunes hung 4 of 6 (`:104-105`).

The load-bearing sentence for this page is at `:215-218`:

> **there is no correct event waiting at the end of the loop.** PYTHIA cannot
> generate these events.

The hang-triggering configurations are not events the campaign threw away. They
are events the generator cannot produce at all.

## 3. The consequence — and the one thing this checkout cannot show

**The argument.** A wedged job is killed and discarded whole; no partial output
is promoted (`config/cr_holdout_policy_v1.json:11`). The missing logical slot is
regenerated **under a new deterministic seed** derived from campaign, tune,
logical job and attempt (`:12`). So the events the discarded job had already
produced were an unbiased draw from the generator, and their replacements are
an equivalent draw from the same generator under a different seed. Neither
carries a bias, because neither was selected on any property of its events.

What is systematically absent, therefore, is not the discarded job's events. It
is the hang-triggering events themselves — and by §2 those are absent from
PYTHIA's reachable output whether or not this campaign ever ran.

**The gap, stated rather than assumed.** The policy's own language is "A failed
**or guard-terminated** attempt promotes no ROOT file" (`:11`). That phrasing
covers two different things: a job wedged in `splitJunGluons`, and a job
terminated by a guard for any other reason. The distinction matters, and **this
checkout cannot resolve it.** `docs/REPRODUCIBILITY.md:147` says so directly:

> The external ledger and attempt metadata are absent. This checkout cannot
> independently derive those discard counts or rates.

So the artifacts here support "127 attempts were discarded and the campaign
record attributes the mechanism to the junction hang". They do **not** support
"each of the 127 was individually confirmed to be wedged in `splitJunGluons`".
The pilot study established the mechanism on four jobs it traced directly; the
production attribution is by rate and by tune, not per attempt.

**Why the bound survives the gap anyway.** Suppose some discards were healthy
jobs terminated by a guard rather than wedged. Such a job contributes *no*
systematically absent event — it would have completed given time, and its
replacement draw is equivalent. Treating all 127 as hang-triggering is
therefore the **conservative** reading, and the bound in §4 is an upper bound
under either interpretation. What the gap costs is the stronger sentence "every
discard was a wedge", which this page does not claim and the manuscript should
not either.

Closing the gap would require the external attempt ledger — per attempt, its
termination cause and its exit path — which is not in this repository.

## 4. The bound

Inputs, each cited:

- delivered sample: 1,000 canonical slots per tune × 100,000 successful events
  per job × 3 tunes = **3 × 10⁸ events**
  ([../paper/CAMPAIGN_TRUTH.md](../paper/CAMPAIGN_TRUTH.md) `:72`);
- discarded attempts: **127** (`config/cr_holdout_policy_v1.json:5-9`);
- hang-triggering events per wedged job: **at most one**, because the job never
  proceeds past the event it wedged on
  (`results/validation/generator/PYTHIA_JUNCTION_HANG_20260731.md:13-15`,
  `:215-218`).

The arithmetic: 127 ÷ 3 × 10⁸ = **4.2 × 10⁻⁷**.

So at most of order one event in two million is absent from the sample for a
reason correlated with the physics, against an attempt attrition of 4.06 %. The
two numbers differ by five orders of magnitude because they count different
things: the percentage counts **jobs**, the bound counts **events**.

## 5. Promotion is conditioned on completion, not on the events

`config/cr_holdout_policy_v1.json`, `handling`:

- `promotion` (`:11`) — "A failed or guard-terminated attempt promotes no ROOT
  file."
- `retry` (`:12`) — "A missing logical slot is regenerated with a new
  deterministic seed derived from campaign, tune, logical job, and attempt."
- `analysis` (`:13`) — "Only promoted complete outputs named by the sealed
  canonical manifest enter reduction."
- `reporting` (`:14`) — "Attempt attrition is disclosed as measured and is not
  corrected away or converted into an event weight."

No key names any property of the generated events. The condition is completion
and manifest membership. That is what makes the replacement draw equivalent
rather than merely similar: nothing in the promotion path can prefer one event
population over another, because nothing in the promotion path reads the
events.

The manifest builder's own ordering supports the same point:
`docs/REPRODUCIBILITY.md:143` records that it "orders promoted logical
identifiers before assigning canonical slots. It never selects the first jobs
to finish."

## 6. What this does not establish

Stated plainly, because a page that argues one thing and is read as arguing
more is worse than no page.

1. **It does not establish that every discard was a wedge.** See §3. The
   artifacts support the mechanism and the rate; they do not carry per-attempt
   termination causes.
2. **It does not measure a bias.** It bounds the population that could carry
   one. A bound is not a measurement, and no variation of the observable was
   computed under a discard model.
3. **It says nothing about systematic uncertainties.** Those are paused under
   ruling R31 and are the subject of
   [../decisions/OPEN_QUESTIONS.md](../decisions/OPEN_QUESTIONS.md) item 1.
4. **It does not address the physics of the excluded region.** PYTHIA cannot
   generate the hang-triggering configurations, so no analysis of this campaign
   can say what they would have contributed. That is a limitation of the
   generator at these settings, and it belongs in the manuscript as one.
5. **It is unratified.** No owner or supervisor has signed it. Ruling R41
   accepts and discloses the hang rate; it does not accept this argument, which
   did not exist when R41 was made.
