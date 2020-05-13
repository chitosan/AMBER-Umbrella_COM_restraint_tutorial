#!/usr/bin/env python
import sys
import os.path
import argparse
import math
import numpy as np

################################################################################
# Simple script to create COM_dist.RST from pdb file of drug molecule
# (must be first residue) and lipid bilayer.
# Assumes PDB is in format as output from ambpdb.
# IMPORTANT: Membrane bilayer center of mass is defined by N31 head group atoms.
################################################################################

##### Parse input line
parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="Drug-bilayer PDB input")
parser.add_argument("-o", type=str, help="Output RST file")

# Required inputs
input_sys=None
output=None

# Check command line arguments exist 
if len(sys.argv)<2:
	parser.print_help()
	sys.exit(1)
elif len(sys.argv)>=2:
	args = parser.parse_args()
	if (args.i != None):
		if os.path.isfile(args.i):
			input_sys=args.i
		elif (not os.path.isfile(args.i)):
			print('Cannot find file: ' % (args.i))
			sys.exit(1)
	else:
		parser.print_help()
		sys.exit(1)

	if args.o != None:
		output=args.o
	else:
		print('Output file name not specified, setting to COM_dist.RST.')
		output='COM_dist.RST'

################################################################################

# zero arrays of arbitrary size - you may need to increase size for a 
# large system
drug=np.zeros(1000)
headgroup=np.zeros(10000)
i=0
j=0

# Save index of drug atoms and lipid N31 atoms 
res=1
atom=1
f = open(input_sys,'r')
lines=f.readlines()[1:]
for line in lines:
	if line[0:3] == "TER":
		res+=1
	else:
		if res==1:
			drug[i]=atom
			i+=1
		elif 'N31' in line[11:22]:
			headgroup[j]=atom
			j+=1
		#elif 'P31' in line[11:22]:
		#	headgroup[j]=atom
		#	j+=1
		atom+=1
f.close()

# Write out .RST file
print('Writing file: %s' % (output))

f_out=open(output,'w')

f_out.write('&rst'+'\n')
f_out.write('iat=-1,-1,'+'\n')
f_out.write('r1=-99.0,'+'\n')
f_out.write('r2=DISTHERE,'+'\n')
f_out.write('r3=DISTHERE,'+'\n')
f_out.write('r4=99.0,'+'\n')
f_out.write('rk2=2.5,'+'\n')
f_out.write('rk3=2.5,'+'\n')
f_out.write('iresid=0,'+'\n')
f_out.write('fxyz=0,0,1,'+'\n')
f_out.write('outxyz=1,'+'\n')
f_out.write('igr1=')

for i in range(0,len(drug)):
	if drug[i]!=0:
		f_out.write(str(int(drug[i]))+',')

f_out.write('\n')
f_out.write('igr2=')

for i in range(0,len(headgroup)):
        if headgroup[i]!=0:
                f_out.write(str(int(headgroup[i]))+',')
f_out.write('\n')
f_out.write('/')
f_out.write('\n')

f_out.close()
