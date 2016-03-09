#!/bin/bash

for i in $(seq 32.0 -2.0 0.0)
do

echo "$i"

cd ./dist_${i}

awk '{print $1,"",$7}' 06_Prod_dist.dat > prod_dist.dat

cd ../

done
