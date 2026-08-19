# Hadronization -- top-level entry point.
#
# Everything machine-specific lives in config/dependencies.local.conf, which is
# untracked. Nothing in this file, or in any tracked script, contains a path
# that only works on one machine. See docs/WORKSPACE.md.
#
#   make help          what you can run
#   make doctor        report what is and is not resolvable here
#   make setup         create config/dependencies.local.conf from the example
#   make build         build the producer
#   make test          run the Python contract tests
#   make check         doctor + cards + registry + tests
#   make submit-prelim render the 4-tune preliminary submit (50 jobs x 100k)
#   make submit-full   render the 4-tune full submit  (1000 jobs x 100k)

SHELL := /bin/bash
ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

# Campaign shape. Override on the command line, e.g.
#   make submit-full CAMPAIGN=HF_RUN3_V1 JOBS=1000 EVENTS=100000
# Production compares the three published tunes. JUNCTIONS_MATCHED exists as
# a card and the producer accepts it, but eight downstream components still
# assume exactly these three, so it is not run.
TUNES        ?= MONASH JUNCTIONS CLOSEPACKING
JOBS         ?= 1000
EVENTS       ?= 100000
PRELIM_JOBS  ?= 50
SMOKE_JOBS   ?= 10
CAMPAIGN     ?= HF_RUN3_PRELIM
# Campaign ordinal. DELIBERATELY NO DEFAULT -- see RELEASE_BLOCKERS.md B11 and
# docs/DESIGN_AND_RATIONALE.md "Campaign ordinals". A default of 1 silently
# stamped every campaign whose operator forgot to set it, which is how HF_PT2,
# HF_SMOKE2 and PTHAT2 all came to carry ordinal 1. The ordinal is packed into
# every event ID and cannot be corrected after the jobs run, so the submit
# targets refuse rather than guess.
ORDINAL      ?=
SEED_LEDGER  ?= $(ROOT_DIR)/config/burned_seeds.txt
# Hang guard. CPU time is the discriminating variable, not wall time: a wedged
# generator burns CPU at ~97%, while a healthy job on a contended node can take
# arbitrarily long in wall clock (one smoke-test job ran at CPU/wall = 0.33).
# Measured CPU per 100k-event job, HF_PT2_INT cluster 5319282, n=292,
# 2026-08-04: MONASH 377s mean / 649s max, JUNCTIONS 659s / 1046s,
# CLOSEPACKING 989s / 1387s. These supersede the earlier 247/480/677s
# medians, which understated the means by 1.4-1.5x; the campaign cost that
# follows from them lives in REPRODUCIBILITY.md section 6, so it stays
# written down somewhere other than a comment beside a guard constant.
# CLOSEPACKING's real headroom against this guard is 2.6x, not the ~4.7x the
# old figures implied. MAX_CPU is deliberately generous:
# the hang is unbounded so any threshold catches it, whereas a tight cut also
# discards slow-but-legitimate jobs -- and dense-junction events are both
# slower AND the ones that make the baryons being measured, so cutting them
# would bias the observable. MAX_RUNTIME is only a backstop for a job stuck
# without burning CPU at all.
MAX_CPU      ?= 3600
MAX_RUNTIME  ?= 14400
# Attempt index for a retry (resubmit). SUBMIT_ATTEMPT is for a fresh submit:
# seeds derive from (tune, job, attempt) and are global across campaigns, so
# re-running the same shape needs a new attempt or the ledger refuses it.
ATTEMPT        ?= 1
SUBMIT_ATTEMPT ?= 0
FREEZE_DIR   ?= $(ROOT_DIR)/campaigns/$(CAMPAIGN)/freeze

# By default the renderer hashes the built producer, so you cannot queue jobs
# against a binary that does not exist. Override only to render a submit on a
# machine where the producer is not built (inspection, or a binary built
# elsewhere); the worker re-checks the hash and refuses a mismatch.
PRODUCER_SHA ?=
PRODUCER_SHA_FLAG := $(if $(PRODUCER_SHA),--producer-executable-sha256 $(PRODUCER_SHA),)

TUNE_FLAGS := $(foreach t,$(TUNES),--tune $(t))
PYTHON     ?= python3

.PHONY: help doctor setup build test cards registry check docs-check \
        submit-smoke submit-prelim submit-full require-ordinal \
        cards-current set-pthat env-verdict \
        status resubmit manifest clean-work print-config

help:
	@echo "Hadronization -- available targets"
	@echo
	@echo "  make doctor         report resolvable dependencies and paths"
	@echo "  make setup          create config/dependencies.local.conf"
	@echo "  make build          build the producer (needs ROOT + PYTHIA)"
	@echo "  make test           run the Python contract tests"
	@echo "  make cards          validate the tune cards"
	@echo "  make cards-current  check every card matches config"
	@echo "  make set-pthat PTHAT=2.0   change the threshold everywhere"
	@echo "  make registry       check generated registry artifacts are current"
	@echo "  make check          doctor + cards + registry + test"
	@echo
	@echo "  make submit-smoke   render smoke submit ($(SMOKE_JOBS) jobs x $(EVENTS) x $(words $(TUNES)) tunes)"
	@echo "  make submit-prelim  render preliminary submit ($(PRELIM_JOBS) jobs x $(EVENTS) x $(words $(TUNES)) tunes)"
	@echo "  make submit-full    render full submit ($(JOBS) jobs x $(EVENTS) x $(words $(TUNES)) tunes)"
	@echo
	@echo "  make status         jobs started / succeeded / unsuccessful"
	@echo "  make resubmit       resubmit jobs with no output (dry run; APPLY=1 to act)"
	@echo "  make manifest       build the canonical manifest for analysis"
	@echo
	@echo "  Override: CAMPAIGN= ORDINAL= JOBS= EVENTS= TUNES= MAX_CPU= MAX_RUNTIME="
	@echo "  Current:  CAMPAIGN=$(CAMPAIGN) JOBS=$(JOBS) EVENTS=$(EVENTS)"
	@echo "            TUNES=$(TUNES)"

print-config:
	@echo "ROOT_DIR    = $(ROOT_DIR)"
	@echo "CAMPAIGN    = $(CAMPAIGN)  (ordinal $(ORDINAL))"
	@echo "TUNES       = $(TUNES)"
	@echo "JOBS        = $(JOBS) x $(EVENTS) events"
	@echo "SEED_LEDGER = $(SEED_LEDGER)"

# doctor never fails: its job is to tell you what is missing, not to stop.
doctor:
	@$(ROOT_DIR)/tools/doctor.sh

setup:
	@if [ -f "$(ROOT_DIR)/config/dependencies.local.conf" ]; then \
	  echo "config/dependencies.local.conf already exists; leaving it alone."; \
	else \
	  cp "$(ROOT_DIR)/config/dependencies.local.conf.example" \
	     "$(ROOT_DIR)/config/dependencies.local.conf"; \
	  echo "Created config/dependencies.local.conf -- edit it, then 'make doctor'."; \
	fi

build:
	@$(ROOT_DIR)/tools/build_producer.sh "$(ROOT_DIR)"

# tools/run_tests.sh sources setupEnv.sh itself, so `make check` is correct on
# the cluster without a memorised prologue. It has to be a script: sourcing
# inside a multi-line make recipe loses the environment across the backslash
# continuations (with `;`, with `&&`, and with .ONESHELL alike), while the same
# prologue works in a single-line recipe. `doctor` and `build` already delegate
# to scripts for their own reasons.
test:
	@PYTHON=$(PYTHON) $(ROOT_DIR)/tools/run_tests.sh "$(ROOT_DIR)"
cards:
	@$(PYTHON) $(ROOT_DIR)/tools/validate_tune_cards.py --root "$(ROOT_DIR)"

# Shared card settings are declared once, in the common_required_card_values
# block of config/tune_difference_allowlist_v1.json. These targets read that
# block and propagate it, rather than leaving four cards, a generated registry
# and a pinned checksum to be edited by hand and discovered one at a time.
cards-current:
	@$(PYTHON) $(ROOT_DIR)/tools/apply_card_config.py --check

set-pthat:
	@test -n "$(PTHAT)" || { echo "usage: make set-pthat PTHAT=2.0"; exit 2; }
	@$(PYTHON) $(ROOT_DIR)/tools/apply_card_config.py \
	  --set PhaseSpace:pTHatMin=$(PTHAT) --apply
	@echo "Now: make build   (the producer embeds the registry checksums)"

registry:
	@$(PYTHON) $(ROOT_DIR)/tools/generate_registry_artifacts.py --check

# Advisory only, never fails: which document owns the areas you just changed.
# See "Which document owns what" in README.md.
docs-check:
	@$(ROOT_DIR)/tools/docs_check.sh "$(ROOT_DIR)"

# `check` ends with the environment verdict, deliberately LAST so it is the
# last thing printed, and it FAILS on an off-pin runtime unless the operator
# declares HF_ALLOW_UNPINNED_ENV=1. See tools/environment_verdict.sh for why a
# green suite on an unpinned host was the defect, not the feature (A7).
check: doctor cards cards-current registry test env-verdict

env-verdict:
	@$(ROOT_DIR)/tools/environment_verdict.sh "$(ROOT_DIR)"

# Submission. The renderer derives seeds deterministically, refuses a seed the
# ledger has already burned, and refuses to render from a dirty checkout.

# Every submit target demands an explicit ordinal. Not only submit-full: the
# ordinal is stamped into event IDs by all three, and a default that is right
# for none of them is what produced the collision in the first place.
require-ordinal:
	@if [ -z "$(strip $(ORDINAL))" ]; then \
	  echo "ERROR: ORDINAL is not set, and there is deliberately no default."; \
	  echo "  The campaign ordinal is packed into every event ID and cannot be"; \
	  echo "  corrected once the jobs have run."; \
	  echo "  Already in use: 1 (HF_PT2, HF_SMOKE2, PTHAT2), 2 (HF_PT2_INT)."; \
	  echo "  HF_RUN3_V1 is ordinal 3."; \
	  echo "  Re-run as: make $(or $(MAKECMDGOALS),<target>) ORDINAL=3"; \
	  exit 1; \
	fi

submit-smoke: require-ordinal
	@$(PYTHON) $(ROOT_DIR)/tools/render_production_submit.py \
	  "$(ROOT_DIR)" "$(ROOT_DIR)/submit_$(CAMPAIGN)_smoke.sub" \
	  --campaign "$(CAMPAIGN)" --campaign-ordinal $(ORDINAL) \
	  $(TUNE_FLAGS) --jobs $(SMOKE_JOBS) --events $(EVENTS) \
	  --attempt $(SUBMIT_ATTEMPT) \
	  --seed-ledger "$(SEED_LEDGER)" --burn-seeds \
	  --max-runtime-seconds $(MAX_RUNTIME) --max-cpu-seconds $(MAX_CPU) \
	  $(PRODUCER_SHA_FLAG)
	@echo "Submit with: condor_submit submit_$(CAMPAIGN)_smoke.sub"

# SEED BURNING -- all three submit targets burn. B2.
#
# The decision, written down because the previous asymmetry (smoke burned,
# prelim and full did not) read as an accident and there was no comment
# anywhere saying which it was:
#
#   ALL THREE BURN. A prelim run produces real data with real seeds; if it does
#   not burn, a later campaign at the same attempt can draw the same seeds and
#   assert_seeds_unused passes because nothing was written. There is no
#   principled reason for the 50-job target to be the one that skips when the
#   10-job and 1000-job targets do not.
#
# Burning happens at RENDER time, not submit time, and that is deliberate:
# a rendered-but-unsubmitted .sub has already reserved its seeds, so a re-render
# cannot silently reuse them. Burning at submit time would leave a window in
# which two renders hand out the same seeds. See tools/campaign.py burn_seeds.
submit-prelim: require-ordinal
	@$(PYTHON) $(ROOT_DIR)/tools/render_production_submit.py \
	  "$(ROOT_DIR)" "$(ROOT_DIR)/submit_$(CAMPAIGN)_prelim.sub" \
	  --campaign "$(CAMPAIGN)" --campaign-ordinal $(ORDINAL) \
	  $(TUNE_FLAGS) --jobs $(PRELIM_JOBS) --events $(EVENTS) \
	  --attempt $(SUBMIT_ATTEMPT) \
	  --seed-ledger "$(SEED_LEDGER)" --burn-seeds \
	  --max-runtime-seconds $(MAX_RUNTIME) \
	  --max-cpu-seconds $(MAX_CPU) $(PRODUCER_SHA_FLAG)
	@echo "Submit with: condor_submit submit_$(CAMPAIGN)_prelim.sub"

submit-full: require-ordinal
	@$(PYTHON) $(ROOT_DIR)/tools/render_production_submit.py \
	  "$(ROOT_DIR)" "$(ROOT_DIR)/submit_$(CAMPAIGN)_full.sub" \
	  --campaign "$(CAMPAIGN)" --campaign-ordinal $(ORDINAL) \
	  $(TUNE_FLAGS) --jobs $(JOBS) --events $(EVENTS) \
	  --attempt $(SUBMIT_ATTEMPT) \
	  --seed-ledger "$(SEED_LEDGER)" --burn-seeds \
	  --max-runtime-seconds $(MAX_RUNTIME) \
	  --max-cpu-seconds $(MAX_CPU) $(PRODUCER_SHA_FLAG)
	@echo "Submit with: condor_submit submit_$(CAMPAIGN)_full.sub"

# Work directories only. Never touches raw output.
clean-work:
	@root="$${HF_PRODUCTION_ROOT:-$(ROOT_DIR)/Production}"; \
	echo "Removing work directories under $$root"; \
	find "$$root" -maxdepth 3 -type d -name work -prune -print -exec rm -rf {} + 2>/dev/null || true

# Accounting. Reads only what the worker wrote on disk, so it cannot drift.
status:
	@$(PYTHON) $(ROOT_DIR)/tools/campaign_status.py "$(CAMPAIGN)" \
	  --expected-jobs $(SMOKE_JOBS)

status-full:
	@$(PYTHON) $(ROOT_DIR)/tools/campaign_status.py "$(CAMPAIGN)" \
	  --expected-jobs $(JOBS)

# Dry run by default: removing held jobs from the queue is irreversible.
# APPLY=1 to actually remove them and render the retry submit.
resubmit:
	@$(PYTHON) $(ROOT_DIR)/tools/resubmit_held.py "$(CAMPAIGN)" \
	  --jobs $(SMOKE_JOBS) --events $(EVENTS) --attempt $(ATTEMPT) \
	  --checkout "$(ROOT_DIR)" --seed-ledger "$(SEED_LEDGER)" \
	  --max-runtime-seconds $(MAX_RUNTIME) --max-cpu-seconds $(MAX_CPU) \
	  $(if $(APPLY),--apply,) $(if $(CLUSTER),--cluster $(CLUSTER),)

manifest:
	@$(PYTHON) $(ROOT_DIR)/tools/build_canonical_manifest.py "$(CAMPAIGN)" \
	  "$(FREEZE_DIR)"

# The checkout freeze, as mechanism rather than memory. Run this on the host
# that has condor_q, BEFORE advancing the Nikhef checkout by any means -- fetch,
# merge, pull, checkout. It refuses while jobs are in flight, and refuses when it
# cannot tell.
#
# The invariant is not about campaigns: jobs in flight that pin a commit => the
# checkout does not move. Production verifies its pinned commit at startup,
# analysis at promotion. Moving the checkout under either invalidates work
# already done -- which is how 2702 v3 analysis jobs came to be re-run.
#
#   make can-advance                               # may I advance?
#   make can-advance REASON="restoring pin 61fe978"  # deliberate override
can-advance:
	@$(PYTHON) $(ROOT_DIR)/tools/checkout_advance_guard.py \
	  $(if $(REASON),--override-reason "$(REASON)",)
