#!/bin/bash

# runCondorJob_ssbar.sh
# Usage: runCondorJob_ssbar.sh <JOBID>

# Load ALICE + Pythia + ROOT env
cd /data/alice/ipardoza/HRP_clean/Code
source ./setupEnv.sh

JOBID=$1

export WORKINGDIR=/data/alice/ipardoza/HRP_clean/Code
export LOG_FILES_DIR=/data/alice/ipardoza/HRP_clean/logs
outdir=/data/alice/ipardoza/HRP_clean/RootFiles/ssbar/MONASH/job_${JOBID}

mkdir -p "${outdir}"
mkdir -p "${LOG_FILES_DIR}"

cd "${WORKINGDIR}" || { echo "Cannot cd to ${WORKINGDIR}"; exit 1; }

echo "Working directory : ${WORKINGDIR}"
echo "Output directory  : ${outdir}"
echo "Job ID            : ${JOBID}"

pwd
ls

echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
source compile.sh
./generate.sh "${JOBID}"
echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"

mv ssbar_monash_job${JOBID}.root "${outdir}/"

echo "Files in output directory (${outdir}):"
ls "${outdir}"

echo "Done! Enjoy!"
