#!/bin/bash

export CUDA_VISIBLE_DEVICES="0"

export prmtop=DMPC_MOH.prmtop
export name=DMPC_MOH

$AMBERHOME/bin/pmemd.cuda -O -i 01_Min.in -o 01_Min.out -p $prmtop -c ${name}.inpcrd -r 01_Min.rst

$AMBERHOME/bin/pmemd.cuda -O -i 02_Heat.in -o 02_Heat.out -p $prmtop -c 01_Min.rst -r 02_Heat.rst -x 02_Heat.nc -ref 01_Min.rst

$AMBERHOME/bin/pmemd.cuda -O -i 03_Heat2.in -o 03_Heat2.out -p $prmtop -c 02_Heat.rst -r 03_Heat2.rst -x 03_Heat2.nc -ref 02_Heat.rst

$AMBERHOME/bin/pmemd.cuda -O -i 04_Equil.in -o 04_Equil_${name}.out -p $prmtop -c 03_Heat2.rst -r 04_Equil_${name}.rst -x 04_Equil_${name}.nc -inf 04_Equil_${name}.mdinfo

$AMBERHOME/bin/pmemd.cuda -O -i 05_Pull.in -o 05_Pull_${name}.out -p $prmtop -c 04_Equil_${name}.rst -r 05_Pull_${name}.rst -x 05_Pull_${name}.nc -inf 05_Pull_${name}.mdinfo
