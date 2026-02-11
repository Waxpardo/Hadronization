# Makefile for heavy-quark correlations (ccbar, bbbar)

CXX      := g++

ROOT_CXXFLAGS := $(shell root-config --cflags)
ROOT_LIBS     := $(shell root-config --libs)

# Try pythia8-config; if not found, fall back to $PYTHIA8
PYTHIA8_CONFIG := $(shell command -v pythia8-config 2>/dev/null)

ifeq ($(PYTHIA8_CONFIG),)
  PYTHIA_CXXFLAGS := -I$(PYTHIA8)/include
  PYTHIA_LIBS     := -L$(PYTHIA8)/lib -lpythia8
else
  PYTHIA_CXXFLAGS := $(shell pythia8-config --cxxflags)
  PYTHIA_LIBS     := $(shell pythia8-config --libs)
endif

CXXFLAGS := -O2 -std=c++17 -Wall -Wextra -pedantic $(ROOT_CXXFLAGS) $(PYTHIA_CXXFLAGS)
LDFLAGS  := $(ROOT_LIBS) $(PYTHIA_LIBS)

all: bbbarcorrelations_status bbbarcorrelations_status_JUNCTIONS \
     ccbarcorrelations_status ccbarcorrelations_status_JUNCTIONS

bbbarcorrelations_status: bbbarcorrelations_status.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

bbbarcorrelations_status_JUNCTIONS: bbbarcorrelations_status_JUNCTIONS.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

ccbarcorrelations_status: ccbarcorrelations_status.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

ccbarcorrelations_status_JUNCTIONS: ccbarcorrelations_status_JUNCTIONS.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f bbbarcorrelations_status bbbarcorrelations_status_JUNCTIONS \
	      ccbarcorrelations_status ccbarcorrelations_status_JUNCTIONS
