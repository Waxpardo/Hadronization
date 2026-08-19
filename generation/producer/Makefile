# Makefile for heavy-quark correlations (split + unified HF)

CXX      := g++

ROOT_CONFIG    := $(shell command -v root-config 2>/dev/null)
PYTHIA8_CONFIG := $(shell command -v pythia8-config 2>/dev/null)

# Do not require external tools for "make clean".
ifneq ($(MAKECMDGOALS),clean)

ifeq ($(ROOT_CONFIG),)
  $(error root-config not found. Load the ROOT environment first, for example with "source ../setupEnv.sh")
endif

ROOT_CXXFLAGS_RAW := $(shell $(ROOT_CONFIG) --cflags)
# Keep strict diagnostics for project sources while treating the pinned
# third-party ROOT headers as system headers. Otherwise -Wconversion warnings
# inside ROOT/PYTHIA can falsely fail the zero-project-warning Gate-A build.
ROOT_CXXFLAGS := $(patsubst -I%,-isystem %,$(ROOT_CXXFLAGS_RAW))
# Link only the ROOT components used by the event producer.  The generic
# `root-config --libs` set also pulls in RDataFrame/Arrow, which is unrelated
# to production and makes non-interactive batch builds depend on a much larger
# alienv runtime.
ROOT_LIBDIR   := $(shell $(ROOT_CONFIG) --libdir)
ROOT_LIBS     := -L$(ROOT_LIBDIR) -lTree -lHist -lRIO -lCore \
                 $(shell $(ROOT_CONFIG) --auxlibs)

# Prefer the explicit PYTHIA8 environment path because some cluster
# pythia8-config scripts exist but do not return usable flags.
#
# The rpath is not optional.  Without it, PYTHIA resolution falls back to
# LD_LIBRARY_PATH ordering, and a producer compiled against one PYTHIA's
# headers will silently load a different PYTHIA's shared object.  That failure
# is near-silent: it surfaces only as a "has different size in shared object"
# note on stderr, after which the process keeps running with a mismatched
# vtable layout.  Binding the build-time PYTHIA into the binary makes the
# mismatch impossible rather than merely unlikely.
ifneq ($(strip $(PYTHIA8)),)
  PYTHIA_CXXFLAGS := -isystem $(PYTHIA8)/include
  PYTHIA_LIBS     := -L$(PYTHIA8)/lib -lpythia8 -Wl,-rpath,$(PYTHIA8)/lib
else ifneq ($(PYTHIA8_CONFIG),)
  PYTHIA_CXXFLAGS_RAW := $(shell $(PYTHIA8_CONFIG) --cxxflags 2>/dev/null)
  PYTHIA_CXXFLAGS := $(patsubst -I%,-isystem %,$(PYTHIA_CXXFLAGS_RAW))
  PYTHIA_LIBS     := $(shell $(PYTHIA8_CONFIG) --libs 2>/dev/null)
else
  $(error Neither PYTHIA8 nor pythia8-config is available. Load the PYTHIA8 environment first, for example with "source ../setupEnv.sh")
endif

endif

# The generated registry headers live in generation/registries/, not beside the
# producer: the 2026-08-12 restructure moved them there (RENAMES.md 1.1) and
# this Makefile was not updated, so it demanded GeneratedHeavyFlavourRegistry.h
# in this directory and stopped with "No rule to make target". The producer
# includes them by bare name, so the location has to be an include directory as
# well as where the prerequisites are found.
#
# -I, not -isystem: these are project headers and must keep the strict
# diagnostics the pinned ROOT/PYTHIA headers are deliberately exempted from.
REGISTRY_DIR := ../registries
CXXFLAGS := -O2 -std=c++17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
            -I$(REGISTRY_DIR) $(ROOT_CXXFLAGS) $(PYTHIA_CXXFLAGS)
LDFLAGS  := $(ROOT_LIBS) $(PYTHIA_LIBS)

# The four split-chain producers this target used to build moved to
# attic/split_chain/ in the same restructure, so `all` named sources that are
# not here and a bare `make` in this directory failed. The split chain has no
# live consumer; `make build` names the one producer explicitly, and so does
# this.
all: heavyflavourcorrelations_status

PRODUCER_OUTPUT ?= heavyflavourcorrelations_status

heavyflavourcorrelations_status: heavyflavourcorrelations_status.cpp \
                                HeavyFlavourUtils.h \
                                Sha256.h \
                                $(REGISTRY_DIR)/GeneratedHeavyFlavourRegistry.h \
                                $(REGISTRY_DIR)/GeneratedTuneSettingRegistry.h
	$(CXX) $(CXXFLAGS) -o $(PRODUCER_OUTPUT) $< $(LDFLAGS)

clean:
	rm -f heavyflavourcorrelations_status
