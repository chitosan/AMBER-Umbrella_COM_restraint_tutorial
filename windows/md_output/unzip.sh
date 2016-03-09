#!/bin/bash

for i in $(seq 32.0 -2.0 0.0)
do

echo "$i"

tar xvzf dist_${i}.tgz

done
