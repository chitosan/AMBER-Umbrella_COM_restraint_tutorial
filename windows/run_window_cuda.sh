#!/bin/bash

export CUDA_VISIBLE_DEVICES="0"

export prmtop=../DMPC_MOH.prmtop
export name=DMPC_MOH

for i in $(seq 32.0 -2.0 0.0)
do

mkdir dist_${i}
cd ./dist_${i}

cp ../COM_dist.RST .

sed -i "s/DISTHERE/${i}/g" COM_dist.RST

$AMBERHOME/bin/pmemd.cuda -O -i ../06_Prod.in -o 06_Prod_${name}_${i}.out -p $prmtop -c ../frame_${i}.rst -r 06_Prod_${name}_${i}.rst -x 06_Prod_${name}_${i}.nc -inf 06_Prod_${name}_${i}.mdinfo

cd ../

done
