#!/bin/bash

touch master
for i in $(seq 32.0 -2.0 0.0)
do

echo "../md_output/dist_${i}/prod_dist.dat ${i} 5.0" >> master

done

mv master metadata.dat
