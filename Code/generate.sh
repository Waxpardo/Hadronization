#!/bin/bash

# generate.sh
# Usage: ./generate.sh <JOBID>

JOBID=$1

OUTROOT="ssbar_monash_job${JOBID}.root"

echo "==========================================="
echo "  generate.sh : JOBID = ${JOBID}"
echo "  Output file : ${OUTROOT}"
echo "==========================================="

# ssbar_generate expects ONLY the output filename as argument
./ssbar_generate "${OUTROOT}"
