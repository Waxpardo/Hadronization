#!/bin/bash

# Specify the base directory to ensure safety
base_dir="/data/alice/pveen/ProductionsPythia"

i=1
k=0

while [ $i -le 40 ] # number of groups
do
    # Create the directory with proper checks
    mkdir "$base_dir/BatchedOutput/MONASH_BATCH_STATUS$i" || { echo "Failed to create directory"; exit 1; }

    for z in {1..25} # size per group (must be equal to k)
    do
        gcount=$(($z+$k))
	echo "$gcount"
        # Perform the copy with proper checks
        cp -r "$base_dir/output_MONASH_cc_215/Group_$gcount" "$base_dir/BatchedOutput/MONASH_BATCH_STATUS$i/" || { echo "Failed to copy files"; exit 1; }
    done

    k=$((k+25)) # size per group
    # echo "k = $k"
    echo "Batch $i has been created!"

    # Change directory with proper checks
    cd "$base_dir/BatchedOutput/MONASH_BATCH_STATUS$i/" || { echo "Failed to change directory"; exit 1; }

    if [ $i -gt 0 ]
    then
        j=1
        for file in *
        do
            if [ -d "$file" ]; then
                mv -v "$base_dir/BatchedOutput/MONASH_BATCH_STATUS$i/$file" "Group$j" || { echo "Failed to rename files"; exit 1; }
                let j++
            else
                echo "Skipping non-directory file: $file"
            fi
        done
    fi

    cd "$base_dir/BatchedOutput" || { echo "Failed to change directory"; exit 1; }
    let i++
done
