#!/bin/bash

for i in $(seq 32.0 -1.0 0.0)
do

val=$(python auto_covar.py -i ../../md_output/dist_${i}/prod_dist.dat -w 500000 -t 0.002 -skip 100 -v 0 | awk '{print $3}')

echo "$i $val"

done
