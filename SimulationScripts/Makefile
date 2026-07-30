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
ifneq ($(strip $(PYTHIA8)),)
  PYTHIA_CXXFLAGS := -isystem $(PYTHIA8)/include
  PYTHIA_LIBS     := -L$(PYTHIA8)/lib -lpythia8
else ifneq ($(PYTHIA8_CONFIG),)
  PYTHIA_CXXFLAGS_RAW := $(shell $(PYTHIA8_CONFIG) --cxxflags 2>/dev/null)
  PYTHIA_CXXFLAGS := $(patsubst -I%,-isystem %,$(PYTHIA_CXXFLAGS_RAW))
  PYTHIA_LIBS     := $(shell $(PYTHIA8_CONFIG) --libs 2>/dev/null)
else
  $(error Neither PYTHIA8 nor pythia8-config is available. Load the PYTHIA8 environment first, for example with "source ../setupEnv.sh")
endif

endif

CXXFLAGS := -O2 -std=c++17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
            $(ROOT_CXXFLAGS) $(PYTHIA_CXXFLAGS)
LDFLAGS  := $(ROOT_LIBS) $(PYTHIA_LIBS)

all: bbbarcorrelations_status bbbarcorrelations_status_JUNCTIONS \
     ccbarcorrelations_status ccbarcorrelations_status_JUNCTIONS \
     heavyflavourcorrelations_status

bbbarcorrelations_status: bbbarcorrelations_status.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

bbbarcorrelations_status_JUNCTIONS: bbbarcorrelations_status_JUNCTIONS.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

ccbarcorrelations_status: ccbarcorrelations_status.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

ccbarcorrelations_status_JUNCTIONS: ccbarcorrelations_status_JUNCTIONS.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

PRODUCER_OUTPUT ?= heavyflavourcorrelations_status

heavyflavourcorrelations_status: heavyflavourcorrelations_status.cpp \
                                HeavyFlavourUtils.h \
                                Sha256.h \
                                GeneratedHeavyFlavourRegistry.h \
                                GeneratedWeakParentRegistry.h \
                                GeneratedTuneSettingRegistry.h
	$(CXX) $(CXXFLAGS) -o $(PRODUCER_OUTPUT) $< $(LDFLAGS)

clean:
	rm -f bbbarcorrelations_status bbbarcorrelations_status_JUNCTIONS \
	      ccbarcorrelations_status ccbarcorrelations_status_JUNCTIONS \
	      heavyflavourcorrelations_status
