#!/usr/bin/env python
import argparse
import numpy as np
import os
import sys
import os.path

################################################################################
# Simple script to extract windows as restart files
################################################################################

##### Parse input line
parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="Trajectory input")
parser.add_argument("-p", type=str, help="Topology file")
parser.add_argument("-d", type=str, help="Corresponding distance file")
parser.add_argument("-start", type=float, help="Start z-position")
parser.add_argument("-end", type=float, help="End z-position")
parser.add_argument("-space", type=float, help="Z-spacing of windows")

# Required inputs
prmtop=None
traj=None
dist_file=None
start=None
end=None
space=None
tolerance=0.01 # tolerance is hard-coded here

# Check command line arguments exist 
if len(sys.argv)<10:
	parser.print_help()
	sys.exit(1)
elif len(sys.argv)>10:
	args = parser.parse_args()
	if (args.i != None and args.p != None and args.d != None and args.start != None and args.end != None):
		if (os.path.isfile(args.i) and os.path.isfile(args.p) and os.path.isfile(args.d)):
			prmtop=args.p
			traj=args.i	
			dist_file=args.d
			start=args.start
			end=args.end
		elif not os.path.isfile(args.d):
			print('Cannot find: %s' % (args.d))
			sys.exit(1)
		elif not os.path.isfile(args.p):
			print('Cannot find: %s' (args.p))
			sys.exit(1)
		elif not os.path.isfile(args.i):
			print 'Cannot find: %s' (args.i))
			sys.exit(1)
	else:
		parser.print_help()
		sys.exit(1)

	if args.space != None:
		space=args.space
	else:
		print('Spacing not set: using 1 A')
		space=1.0

# Check that AMBERHOME is set
amberhome = os.getenv('AMBERHOME')
if amberhome == None:
        print('Error: AMBERHOME not set')
	sys.exit(1)

# Check that for negative end-point, spacing will descend
if end<0 and space>0:
	space=space*-1
elif end>0 and space<0:
	space=space*-1

# Load file with drug-bilayer C.O.M. distance
dist=np.loadtxt(dist_file,skiprows=1,usecols=(6,))

# Numpy array of points we need to extract
points=np.arange(start,end+space,space)

################################################################################
# Extract relevant frames using cpptraj
for i in xrange(points.shape[0]):
	for j in xrange(dist.shape[0]):
		if (points[i]-tolerance)<dist[j]<(points[i]+tolerance):
			print(points[i],dist[j],j)
			with open('frame_extract.trajin','w') as f:
				f.write('trajin %s %d %d 1 \n' % (traj,j+1,j+1))
				f.write('trajout frame_%.1f.rst restart \n' % (points[i]))
			os.system('$AMBERHOME/bin/cpptraj %s < frame_extract.trajin > out' % prmtop)
			os.system('rm frame_extract.trajin')
			os.system('rm out')
			break
	else:
		print('Empty window: %lf' % (points[i]))
