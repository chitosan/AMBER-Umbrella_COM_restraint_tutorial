#!/bin/bash

for i in $(seq 32.0 -2.0 0.0)
do

val=$(python auto_covar.py -i ../../md_output/dist_${i}/prod_dist.dat -w 50000 -t 0.02 -skip 10 -v 0 | awk '{print $3}')

echo "$i $val"

done
