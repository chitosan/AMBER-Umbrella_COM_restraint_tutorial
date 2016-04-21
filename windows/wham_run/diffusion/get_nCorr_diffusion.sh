#!/bin/bash

# Total ns in dist file
total_ns=5

# Spacing between z-value distances
dt_space=0.02

##############################################################################
# Arithmatic using above settings
##############################################################################

# Calculate lines
full_lines=$(echo "scale=2; $total_ns/$dt_space" | bc)

# Calculate lines needed for 1ns 
lines_1ns=$(echo "scale=0; 1000/${dt_space}" | bc)

# Calculate lines needed for 50ps
lines_50ps=$(echo "scale=2; 50/${dt_space}" | bc)

##############################################################################
# Run loop
# Check that file locations specified below are correct
##############################################################################

for i in $(seq 6.0 -2.0 0.0)
do

if [ -d "dist_${i}" ]; then
	echo "Exit: dist_${i} exists!"
	exit
else

mkdir dist_${i}
cd ./dist_${i}

split --lines=${lines_1ns} ../../../md_output/dist_${i}/prod_dist.dat 1ns_chunk.

for filename in 1ns_chunk.*;
do

../ACF_calc.x -f $filename -s ${lines_1ns} -n ${lines_50ps} -d ${dt_space} -o acf_${filename} >>OUTPUT_ACF

done

val=$(awk '{sum+=$2}END{print sum/NR}' OUTPUT_ACF)
echo "$i $val"

fi

cd ../

done
