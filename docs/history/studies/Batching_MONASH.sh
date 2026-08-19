#!/bin/bash

set -euo pipefail

# Usage:
#   ./SimulationScripts/Batching_MONASH.sh [BASE_DIR] [SOURCE_SUBDIR] [TARGET_SUBDIR]

base_dir="${1:-${BATCHING_BASE_DIR:-/data/alice/pveen/ProductionsPythia}}"
source_subdir="${2:-output_MONASH_cc_215}"
target_subdir="${3:-BatchedOutput}"

i=1
k=0

while [ $i -le 40 ] # number of groups
do
    # Create the directory with proper checks
    mkdir -p "$base_dir/$target_subdir/MONASH_BATCH_STATUS$i" || { echo "Failed to create directory"; exit 1; }

    for z in {1..25} # size per group (must be equal to k)
    do
        gcount=$(($z+$k))
	echo "$gcount"
        # Perform the copy with proper checks
        cp -r "$base_dir/$source_subdir/Group_$gcount" "$base_dir/$target_subdir/MONASH_BATCH_STATUS$i/" || { echo "Failed to copy files"; exit 1; }
    done

    k=$((k+25)) # size per group
    # echo "k = $k"
    echo "Batch $i has been created!"

    # Change directory with proper checks
    cd "$base_dir/$target_subdir/MONASH_BATCH_STATUS$i/" || { echo "Failed to change directory"; exit 1; }

    if [ $i -gt 0 ]
    then
        j=1
        for file in *
        do
            if [ -d "$file" ]; then
                mv -v "$base_dir/$target_subdir/MONASH_BATCH_STATUS$i/$file" "Group$j" || { echo "Failed to rename files"; exit 1; }
                let j++
            else
                echo "Skipping non-directory file: $file"
            fi
        done
    fi

    cd "$base_dir/$target_subdir" || { echo "Failed to change directory"; exit 1; }
    let i++
done
