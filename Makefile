# Top-level command interface.
# Machine-specific dependency overrides belong in the untracked
# config/dependencies.local.conf file.
#
#   make help          what you can run
#   make doctor        report what is and is not resolvable here
#   make setup         create config/dependencies.local.conf from the example
#   make build         build the producer
#   make test          run the Python contract tests
#   make check         doctor + cards + registry + tests
#   make submit-prelim render the 3-tune preliminary submit (50 jobs x 100k)
#   make submit-full   render the 3-tune full submit  (1000 jobs x 100k)

SHELL := /bin/bash
ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

# Override the campaign shape on the command line.
#   make submit-full CAMPAIGN=HF_RUN3_V1 JOBS=1000 EVENTS=100000
# Production compares the three published tunes. JUNCTIONS_MATCHED exists as
# a tune card, but the publication chain enumerates the three published tunes.
TUNES        ?= MONASH JUNCTIONS CLOSEPACKING
JOBS         ?= 1000
EVENTS       ?= 100000
PRELIM_JOBS  ?= 50
SMOKE_JOBS   ?= 10
CAMPAIGN     ?= HF_RUN3_PRELIM
# Every submit target needs an explicit campaign ordinal.
# The producer packs the ordinal into each event identifier, so later stages
# cannot correct an implicit value.
ORDINAL      ?=
# Mutable campaign state belongs in the external data plane whenever the site
# profile has been sourced.  The checkout-local fallbacks keep direct Makefile
# development usable, but the root ./hadronization command always exports the
# external Nikhef/local-development data root.
STATE_ROOT   ?= $(if $(HADRONIZATION_DATA_ROOT),$(HADRONIZATION_DATA_ROOT)/project/runs,$(ROOT_DIR)/campaigns)
SEED_LEDGER  ?= $(STATE_ROOT)/seed_ledgers/burned_seeds.txt
# The hang guard uses CPU time because wedged generators continue to consume CPU.
# The 3,600-second limit gives 2.6 times the measured CLOSEPACKING maximum.
# A tight limit could reject slow, baryon-rich events and bias the observable.
# The wall-time limit also catches jobs that stop consuming CPU.
MAX_CPU      ?= 3600
MAX_RUNTIME  ?= 14400
# ATTEMPT selects a retry, while SUBMIT_ATTEMPT selects a fresh submission.
# Seeds derive from the campaign ordinal, tune, job, and attempt.
ATTEMPT        ?= 1
SUBMIT_ATTEMPT ?= 0
FREEZE_DIR   ?= $(STATE_ROOT)/$(CAMPAIGN)/freeze

# The renderer normally calculates the digest of the built producer.
# Set PRODUCER_SHA only when another host supplies that exact binary.
# The worker refuses a binary whose digest differs.
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
	@echo "STATE_ROOT  = $(STATE_ROOT)"

# The doctor reports missing dependencies but does not gate another target.
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

# The test driver sources setupEnv.sh in one shell before it runs the suite.
test:
	@PYTHON=$(PYTHON) $(ROOT_DIR)/tools/run_tests.sh "$(ROOT_DIR)"
cards:
	@$(PYTHON) $(ROOT_DIR)/tools/validate_tune_cards.py --root "$(ROOT_DIR)"

# The allowlist stores settings that all tune cards must share.
# These targets propagate that source into every card and generated registry.
cards-current:
	@$(PYTHON) $(ROOT_DIR)/tools/apply_card_config.py --check

set-pthat:
	@test -n "$(PTHAT)" || { echo "usage: make set-pthat PTHAT=2.0"; exit 2; }
	@$(PYTHON) $(ROOT_DIR)/tools/apply_card_config.py \
	  --set PhaseSpace:pTHatMin=$(PTHAT) --apply
	@echo "Now: make build   (the producer embeds the registry checksums)"

registry:
	@$(PYTHON) $(ROOT_DIR)/tools/generate_registry_artifacts.py --check

# This advisory maps changed paths to their owning documents and never fails.
docs-check:
	@$(ROOT_DIR)/tools/docs_check.sh "$(ROOT_DIR)"

# The final environment verdict rejects an off-pin runtime.
# HF_ALLOW_UNPINNED_ENV=1 limits a green result to source contracts.
check: doctor cards cards-current registry test env-verdict

env-verdict:
	@$(ROOT_DIR)/tools/environment_verdict.sh "$(ROOT_DIR)"

# Submission rendering derives deterministic seeds and rejects used seeds.
# It also rejects a checkout with tracked changes.

# Every submit target requires an ordinal because every target writes event identifiers.
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

# Every submit target reserves its seeds when the renderer writes the submit file.
# Render-time reservation prevents two unsubmitted files from sharing seeds.
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

# This target removes work directories but preserves raw files.
clean-work:
	@root="$${HF_PRODUCTION_ROOT:-$(ROOT_DIR)/Production}"; \
	echo "Removing work directories under $$root"; \
	find "$$root" -maxdepth 3 -type d -name work -prune -print -exec rm -rf {} + 2>/dev/null || true

# Status targets derive their counts from worker outputs.
status:
	@$(PYTHON) $(ROOT_DIR)/tools/campaign_status.py "$(CAMPAIGN)" \
	  --expected-jobs $(SMOKE_JOBS)

status-full:
	@$(PYTHON) $(ROOT_DIR)/tools/campaign_status.py "$(CAMPAIGN)" \
	  --expected-jobs $(JOBS)

# The resubmit target defaults to a dry run because queue removal is irreversible.
# Set APPLY=1 to remove held jobs and render their retries.
resubmit:
	@$(PYTHON) $(ROOT_DIR)/tools/resubmit_held.py "$(CAMPAIGN)" \
	  --jobs $(SMOKE_JOBS) --events $(EVENTS) --attempt $(ATTEMPT) \
	  --checkout "$(ROOT_DIR)" --seed-ledger "$(SEED_LEDGER)" \
	  --max-runtime-seconds $(MAX_RUNTIME) --max-cpu-seconds $(MAX_CPU) \
	  $(if $(APPLY),--apply,) $(if $(CLUSTER),--cluster $(CLUSTER),)

manifest:
	@$(PYTHON) $(ROOT_DIR)/tools/build_canonical_manifest.py "$(CAMPAIGN)" \
	  "$(FREEZE_DIR)"

# The checkout guard requires condor_q and refuses while pinned jobs run.
# It also refuses when it cannot determine the queue state.
# Production checks the commit at startup, while reduction checks it at promotion.
#
#   make can-advance                               # may I advance?
#   make can-advance REASON="restoring pin 61fe978"  # deliberate override
can-advance:
	@$(PYTHON) $(ROOT_DIR)/tools/checkout_advance_guard.py \
	  $(if $(REASON),--override-reason "$(REASON)",)
