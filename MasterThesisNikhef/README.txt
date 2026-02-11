**************************************************************************************
** Heavy flavour azimuthal angular correlation studies in pp collisions with PYTHIA **
**************************************************************************************

Author: Paul Veen (paul.veen@cern.ch)

Presentation with updated (13-05-2025) documentation: https://docs.google.com/presentation/d/1uLaIOoKUsLtDPMpJzauxONb1dARULm3ucuzLlODav8s/edit?usp=sharing

This repository contains C++ scripts that are used to generate and study azimuthal angular
correlations for charm and beauty hadrons in pp collisions with PYTHIA.
The goal of this README is to give some insight in how these scripts work and how they can be
changed in order to reproduce results or to investigate other parameters in these simulations.
First, a short description of all files in this repository is given, and secondly, a short
tutorial is given on how to simulate and analyse events with these scripts.

It is also possible to start with the pre-generated ROOT files, with settings largely similar to
the ones used in the simulation scripts on this repository (but when I have the final simulations
again I'll make sure they are completely consistent).

***********************
** Overview of files **
***********************

** SimulationScripts **
- bbbarcorrelations_status.cpp
- ccbarcorrelations_status.cpp
C++ scripts that are used to generate (bb/cc) events with PYTHIA, the output is given using a
ROOT TTree structure.
These scripts are compiled with the Makefile given in this repository (identical name, omitting
the .cpp suffix).

- pythiasettings_Hard_Low_bb.cmnd
- pythiasettings_Hard_Low_cc.cmnd
cmnd file that contains the settings used in the PYTHIA simulations in the generating scripts.
This avoids having to recompile the C++ scripts after every change.

- MakeFile
Used to compile the .cpp simulation files with the `make` command

** AnalysisScripts **
- status_analysis_bb.C
- status_analysis_cc.C
ROOT C++ macros used to create angular correlation histograms from the generated PYTHIA events.
The histograms are saved and can be subsequently used in local analysis scripts.

** PlottingScripts **
These scripts are given for D+D- and B+B- correlations, but it is also possible to check for other
trigger-associate pairs.

- PlottingComparisonStudy.C
ROOT C++ macro that draws D+D- and B+B- angular correlations for different pT conditions on the
same canvas, including their ratio as a subplot. 

- ProductionOriginStudy.C
ROOT C++ macro that draws D+D- angular correlations divided into the production origin of the trigger (D+)
and associate (D-) as prompt/prompt, non-prompt/non-prompt, or a combination.

- DecayAndHadronisation_Markers_MotherStudy
ROOT C++ macro that draws D+D- angular correlations and the trigger/associate mothers in linear
stacked plots, in order to study the origin of these correlations in more detail.
The other three MotherStudy scripts are very similar in structure, hence the full documentation for
all these macros is only given in the DecayAndHadronisation_Markers_MotherStudy file.

As a reference, this is part of the documentation relevant for the other MotherStudy scripts:
// Comments on other mother study macros:
//
// The other three mother study macros are very similar in structure to this code, hence this
// file will be refered to as the main documentation. There are some differences however, and they
// will be highlighted here.
// 
// DecayAndHadronisation_Stacked_MotherStudy.C -> both prompt and non-prompt production is analysed
// with Delta phi of the trigger and associate particles for low-low and high-high pT regions,
// linear scale is used, stacked plots are shown.
// DecayAndHadronisation_Markers_MotherStudy.C -> same as DecayAndHadronisation_Stacked_MotherStudy.C,
// but with log scale marker plots. The log marker plots allow to visualise even the smallest of
// contributions, while the stacked plots are better at showing the main components of the angular
// correlations.
//
// The non-prompt case is zoomed in on and a study is done on the Delta phi of the mother(s) of the
// trigger and associate, which can be the same mother or a different mother, being the main point
// of this study. There is no classification based on pT regions, as it is not expected to change
// much, but can be added if desired.
// SameDiffMother_Stacked_MotherStudy.C -> for linear stacked plots
// SameDiffMother_Markers_MotherStudy.C -> for log marker plots

** RootFiles **
- DESCRIPTIONS.txt
Some pre-produced ROOT files are given which can be compared or directly used in the analysis
macros to bypass longer and computationally more intense PYTHIA simulations. These ROOT files
have somewhat cryptic names and hence they are (briefly) descriped in this .txt file.

** Other **
- MasterThesis.pdf
PDF file containing, as one can guess, my master thesis (up until the latest version) in order to
get a more in-depth analysis of the results that can be obtained using the simulation, analysis and
plotting scripts given in this repository.

*********************
** Little tutorial **
*********************

For larger simulations (in this tutorial, anything > 1 million events) it is essential to be able
to use some sort of computing cluster to speed up calculations. This code has been written in a
way to work in this way, though it will likely need to be changed for other users.

Suppose we want to generate and analyse cc angular correlations locally. The simulation process
starts with the pythiasettings_Hard_Low_cc.cmnd file, which governs the settings used to generate
the events, as explained in the comments within this file. The settings do not have to be
changed, though the number of events can be increased when using a cluster. 

The first step is to compile the ccbarcorrelations_status_cc.cpp script, which can be done using
the Makefile,
    > Make ccbarcorrelations_status
which will create an executable called ccbarcorrelations_status.

The script can then be run using
      > ./ccbarcorrelations_status "output.root"
that generates an output ROOT file with name output.root

The next step is to create the angular correlation histograms. There are a lot of interesting
possibilities to investigate here, but let's start with the examples that are created in the given
status_analysis_cc.C macro and will be necessary for the D+D- correlations that will be done in
this tutorial.

If the file paths are correct, which is set up to work with the structure of this git
repository, and if the input structure is compatible with the output from the PYTHIA simulations
then the macro is run by typing
       > root status_analysis_cc.C
which will generate an output ROOT file called "DplusDminus.root" containing the angular
correlation histograms and the combined 2-dimensional angular correlations and mother ID
histograms.

The analysis can go in many directions from here, but for now we are interested in plotting what
the D+D- angular correlations look like and what the origin is of our D+ and our D- mesons.
This is done by executing the given ROOT macros found in the PlottingScripts folder, all of which
have the option to save the produced canvases as PDF by changing the bool `write` and making sure
the file path is correct. Initially these paths are set up to take standard examples from the
RootFiles folder, but one can also generate their own PYTHIA outputs and correlations to analyse.

Small note: the given ROOT outputs are generated with older simulation code, which is not consistent
with the code given in this repository.
The given ROOT files will be updated soon when new, and correct, simulation scripts are back (in
particular the pythiasettings_Hard_Low.cmnd files will need attention).
