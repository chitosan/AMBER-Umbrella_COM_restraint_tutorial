#!/usr/bin/env python
import argparse
import numpy as np
import math
import os
import sys
import os.path

################################################################################
# Script to read in free energy, diffusion and output resistance and permeability
# Run as:
# ./parse_fe_diff.py -fe free_energy -diff diffusion -start start_val
#   -end end_val -space space_val -temp temperature_val
#
# Ensure that input fe_file and diff_file have this format:
#
# z-distance fe_value/diff_value
# 
################################################################################

##### Parse input line
parser = argparse.ArgumentParser()
parser.add_argument("-fe", type=str, help="Free energy input")
parser.add_argument("-diff", type=str, help="Diffusion input")
parser.add_argument("-start", type=float, help="Start z-position")
parser.add_argument("-end", type=float, help="End z-position")
parser.add_argument("-space", type=float, help="Z-spacing of windows")
parser.add_argument("-temp", type=float, help="Temperature")

# Required inputs
fe_input=None
diff_input=None
start=None
end=None
space=None
temperature=None
tolerance=0.1 # tolerance is hard-coded here

# Check command line arguments exist 
if len(sys.argv)<12:
	parser.print_help()
	sys.exit(1)
elif len(sys.argv)>12:
	args = parser.parse_args()
	if (args.fe != None and args.diff != None and args.start != None and args.end != None):
		if (os.path.isfile(args.fe) and os.path.isfile(args.diff)):
			fe_input=args.fe
			diff_input=args.diff
			start=args.start
			end=args.end
			temperature=args.temp
		elif not os.path.isfile(args.fe):
			print 'Cannot find: ',args.fe
			sys.exit(1)
		elif not os.path.isfile(args.diff):
			print 'Cannot find: ',args.diff
			sys.exit(1)
	else:
		parser.print_help()
		sys.exit(1)

	if args.space != None and args.space!=0:
		space=args.space
	elif args.space==0:
		print 'Error: cannot use zero spacing'
		sys.exit(1)
	else:
		print 'Spacing not set: using 1 A'
		space=1.0

# Check arguments are set
if fe_input==None or diff_input==None or start==None or end==None or space==None or temperature==None:
	print 'Error: options not set'
	sys.exit(1)

# Check that for negative end-point, spacing will descend
if end<0 and space>0:
	space=space*-1
elif end>0 and space<0:
	space=space*-1

# RT (kcal/K/mol units) 
RT=0.0019858775*temperature

# Check that input file is in correct format
#with open(fe_input) as f_in:
#        line = f_in.readline()
#if len(line.split())>2:
#        print 'Error: input file contains >2 columns'
#        sys.exit(1)

with open(diff_input) as f_in:
	line = f_in.readline()
if len(line.split())>2:
	print 'Error: input file contains >2 columns'
	sys.exit(1)

# Load free energy and diffusion profile files
fe_data=np.loadtxt(fe_input)
diff_data=np.loadtxt(diff_input)

################################################################################
# Main loop
################################################################################

# Numpy array of points we need to extract
points=np.arange(start,end+space,space)
out_perm=np.zeros((points.shape[0],4))

# Save free energy
for i in xrange(points.shape[0]):
	for j in xrange(fe_data.shape[0]):
		if (points[i]-tolerance)<fe_data[j][0]<(points[i]+tolerance):
			#print fe_data[j][0],fe_data[j][1]
			out_perm[i][0]=points[i]
			out_perm[i][1]=fe_data[j][1]
			break

# Save diffusion
for i in xrange(points.shape[0]):
	for j in xrange(diff_data.shape[0]):
		if (points[i]-tolerance)<diff_data[j][0]<(points[i]+tolerance):
			out_perm[i][2]=diff_data[j][1]
			break

# Set free energy to zero in water
for i in xrange(points.shape[0]):
        out_perm[i][1]=(out_perm[i][1]-out_perm[points.shape[0]-1][1])

# Calculate resistance
for i in xrange(points.shape[0]):
	if out_perm[i][2]!=0.0:
		out_perm[i][3]=(math.exp(out_perm[i][1]/RT))/out_perm[i][2]
	else:
		print 'Error: out-of-bounds',points[i]

# Write out resistance
with open('resistance_profile.parse.dat','w') as f:
	for i in xrange(points.shape[0]):
		f.write(str(out_perm[i][0])+' '+str(out_perm[i][3])+'\n')

# Write out free energy 
with open('free_energy_profile.parse.dat','w') as f:
	for i in xrange(points.shape[0]):
		f.write(str(out_perm[i][0])+' '+str(out_perm[i][1])+'\n')

# Write out diffusion 
with open('diffusion_profile.parse.dat','w') as f:
	for i in xrange(points.shape[0]):
		f.write(str(out_perm[i][0])+' '+str(out_perm[i][2])+'\n')

# Print out permeability coefficient
try:
	Reff=np.trapz(out_perm[:,3],dx=(space*1e-8))
	print 'Reff: ',Reff,' Peff: ',(1/Reff),' cm/s'
except:
	print 'Error: could not integrate resistance'

