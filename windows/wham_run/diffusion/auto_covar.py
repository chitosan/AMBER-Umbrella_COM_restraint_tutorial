#!/usr/bin/env python
import math
import numpy
import itertools
import argparse
import sys
import os.path
from scipy.optimize import curve_fit

################################################################################
# Autocovarience with moving time-lag window
################################################################################

##### Parse input line
parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="Input z-position file")
parser.add_argument("-w", type=int, help="Window for fit")
parser.add_argument("-t", type=float, help="Time-step between points (ps)")
parser.add_argument("-skip", type=int, help="Only read only n-frames")
parser.add_argument("-v", type=int, help="Verbose (0/1): print autocovariance curves")

# Required inputs
input_file=None
window=None
timestep=None
get_line=None
print_out=False

# Check command line arguments
if len(sys.argv)<6:
	parser.print_help()
	sys.exit(1)
elif len(sys.argv)>=6:
	args = parser.parse_args()
	if (args.i != None and args.w != None and args.t != None):
		if os.path.isfile(args.i):
			input_file=args.i
			window=args.w
			timestep=args.t
		elif not os.path.isfile(args.i):
			print 'Cannot find file: ',args.i
			sys.exit(1)

	if args.skip!=None:
		get_line=args.skip
		if args.skip==0:
			get_line=None
	else:
		get_line=0

	if args.v!=None:
		print_out=args.v
	else:
		args.v=0

# Check that input file is in correct format
with open(input_file) as f_in:
	line = f_in.readline()
if len(line.split())>2:
	print 'Error: input file contain >2 columns'
	sys.exit(1)

# Check that inputs are set
if input_file==None or window==None or timestep==None:
	print 'Error: options not set'
	sys.exit(1)
	
################################################################################
# Read input
with open(input_file) as f_in:
	data = numpy.genfromtxt(itertools.islice(f_in, 0, None, get_line),usecols=(1,))

if get_line!=None and get_line>0:
	window=window/get_line
	timestep=timestep*get_line

# Time-lag slices of data
slices=int(math.floor(len(data))/window)

################################################################################
# Linear least-squares fit function 
def func(x, b, c):
        return (-b * x + c)

# Function to return autocovariance of two arrays.
# Input: array1, avg_array1, array2, avg_array2, window_size
def autocovariance(Xi, Ai, Xs, As, N):
	autoCov = 0
	for i in xrange(0,N):
		autoCov += (Xi[i]-Ai)*(Xs[i]-As)
	return (autoCov/(N-1)) 

################################################################################
# Main loop
################################################################################

index=0
avg_DZ=0.0
# Loop over slices
for i in range(0,(window*slices)-window,window):
	if print_out>0:
		fout=open('corr.'+str(i/window)+'.dat','w')
	decay_t=numpy.zeros(window)
	decay_y=numpy.zeros(window)
	decay_t_ln=numpy.zeros(window)
	decay_y_ln=numpy.zeros(window)
	corr_zero=0
	for j in xrange(0,window):
		decay_t[j]=(j*timestep)
		decay_y[j]=autocovariance(data[i:window+i],numpy.average(data[i:window+i]),data[i+j:window+i+j],numpy.average(data[i+j:window+i+j]),window)
		# Print autocovariance curves for verbose setting
		if print_out>0:
			fout.write(str(decay_t[j])+' '+str(decay_y[j])+'\n')
		if decay_y[j]>0:
			decay_t_ln[j]=(j*timestep)
			decay_y_ln[j]=numpy.log(decay_y[j])
			# Uncomment (and comment above) to print log curves, which are actually used in the fit
			#if print_out>0:
				#fout.write(str(decay_t_ln[j])+' '+str(decay_y_ln[j])+'\n')
		else:
			break

	if print_out>0:
		fout.close()
	corr_zero=decay_y[0]

	popt, pcov = curve_fit(func, decay_t_ln[:], decay_y_ln[:])
	b=popt[0]
	#print 'tau: ',b
	if b<10:
		avg_DZ+=(((corr_zero*math.pow(10,-20))/((1/b)*math.pow(10,-12)))*math.pow(10,4))
		index+=1
	else:
		#print 'Removed from set: ',b
		pass

print 'Average DZ(cm^2/s): ',avg_DZ/index

