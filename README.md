# AMBER-Umbrella_COM_restraint_tutorial
Tutorial to run AMBER umbrella COM restraint code and derive free energy of transfer profile for methanol through DMPC membrane.

![Alt text](/figures/moh_profile.png?raw=true "Optional Title")

# Requirements:

* AMBER16 or above (has COM umbrella restraint code)
* Python 2.7 (https://www.continuum.io/downloads)
* WHAM (http://membrane.urmc.rochester.edu/content/wham)

# Introduction
This tutorial uses the AMBER16 center-of-mass (COM) umbrella restraint code to determine the free energy of transfer profile for a methanol molecule through a DMPC membrane bilayer. The methanol molecule is first pulled from the center of the membrane out into the water phase. From the pulling step, we extract starting positions with methanol at 0, 1, 2, ..., 32 A from the membrane center. We run windows with methanol restrained at each of these positions. From the fluctuation in the z-position, we can construct the free energy profile using WHAM. Finally, we use the same information to derive the z-diffusion and z-resistance profiles and an estimate of the overall permeability coefficient.

There is a great deal of literature available on running z-restraint simulations, which I would encourage you to consult. A few examples include:

http://pubs.acs.org/doi/abs/10.1021/jp035260s

http://pubs.acs.org/doi/abs/10.1021/jp903248s

http://dx.doi.org/10.1016/j.bpj.2014.06.024

# Step 1: Parameters
First we need a starting membrane bilayer PDB file and the coordinates and parameters for methanol.  
>./parameters directory  

You can follow the AMBER tutorial TUTORIAL A16: An Amber Lipid Force Field Tutorial: Lipid14 to obtain an equilibrated lipid bilayer.

Use antechamber to create AMBER parameters for methanol from the enclosed methanol PDB:

>antechamber -i methanol.pdb -fi pdb -o MOH.mol2 -fo mol2 -c bcc -s 2

Then use tleap to convert the resulting MOH.mol2 into an AMBER library file (MOH.off):

>tleap -f convert.leap

# Step 2: Placement
Next we place the methanol molecule at the center of the membrane (the z-distance between methanol and DMPC bilayer is zero).  
>./placement directory  

A study has shown that pulling from the middle of the membrane out allows faster convergence of PMFs rather than pulling from the water phase into the membrane:

http://pubs.acs.org/doi/abs/10.1021/jp501622d

You can use the python script to place the methanol molecule at z=0 from the DMPC bilayer center-of-mass:

>./com_placement.py -i DMPC_72_relax.pdb -d methanol.pdb -z 0.0 > moh_center.pdb

**Important note:** The com_placement.py script defines the center-of-mass of the membrane using the PC N31 head group atoms in the lipids. It will not work if these are not present: if you wish to use other atoms, you'll have to update the code. Also, if your drug molecule contains unusual atom types, you may need to add the atomic mass of these atoms into the com_placement code.

We can now create AMBER prmtop and inpcrd files of the system. First, to set the periodic box dimensions correctly, we use the vmd_box_dims.sh script from the A16 Lipid tutorial:

>./vmd_box_dims.sh -i DMPC_72_relax.pdb -s water  
>48.158000, 47.372001, 77.938003

Using the output we can build the system with build.leap file shown below:

>source leaprc.ff14SB  
>source leaprc.gaff  
>source leaprc.lipid16  
>loadoff MOH.off  
>drug = loadpdb moh_center.pdb  
>bilayer = loadpdb DMPC_72_relax.pdb  
>system = combine {drug bilayer}  
>set system box {48.158 47.372 77.938}  
>saveamberparm system DMPC_MOH.prmtop DMPC_MOH.inpcrd  
>quit  

Now run tleap:

>tleap -f build.leap

# Step 3: Pulling
Now that we have our system constructed, we first equilibrate it then run a pulling step, which slowly moves the methanol molecule from z=0A out into the water phase (z=32A).  
>./pulling directory  

First, we need the distance restraint file. You can use the make_COM_file.py script to construct this. It contains the atom indices of the drug atoms (group 1 to be constrained) and the atom indices of the lipid N31 head group atoms (reference to constrain to). It also contains details of the harmonic restraint to apply and flags to turn on the umbrella COM method.

First we need a pdb of the system with atom indexing correct:
>ambpdb -p DMPC_MOH.prmtop <DMPC_MOH.inpcrd> for_index.pdb

Now run the script:
>./make_COM_file.py -i for_index.pdb -o ref_COM_file.RST

As an aside, we can also check that we have the correct atom indices directly from the prmtop using parmed. We need an input for parmed, see details_parmed.in:
>parm DMPC_MOH.prmtop  
>printDetails *  
>quit  

Run ParmEd:

>parmed.py -i details_parmed.in > atom_list.out

You can check that in atom_list.out the N31 atom index values corresponds to those in ref_COM_file.RST

Please go through the AMBER manual so that you know what each line in the ref_COM_file.RST means. Important flags are:
>rk2=2.5    *restraint force constant*  
>fxyz=0,0,1 *turn on umbrella COM in z-direction only*  
>outxyz=1   *print position of restrained molecule in x,y,z dimensions*

You may notice that ref_COM_file.RST has settings "DISTHERE" - we will copy this to a new file and add in the correct settings here.
>cp ref_COM_file.RST COM_dist.RST

Change DISTHERE to 0.0 in COM_dist.RST. 

We also need a file for the pulling step COM_pull.RST. This is similar to COM_dist.RST but specifies a starting positon of 0 and a final position of 32, the force constant for pulling is also reduced to 1.1.

We now have the .RST files for equilibration (methanol is held at z=0) and for the pulling (methanol is moved from z=0 to z=32A).

The inputs and run script are provided. Please also examine the input files, importantly:
>&wt type='DUMPFREQ', istep1=1000 /  *print position of restrained molecule every 1000 steps*  
>&wt type='END', /  
>DISANG=COM_dist.RST *details of the COM restraint*  
>DUMPAVE=04_Equil_dist.RST *file to write position of restrained molecule to*  

You can then run both the equilibration (heat, hold methanol at z=0 for 100ps) and the pulling (move methanol from z=0 to z=32A  over 32ns of simulation) with the following bash script:
>./run_pull.sh

You will have to modify GPU / AMBERHOME specific information, or make it suitable for your cluster.

Due to file sizes, the outputs are not provided here. You can check the pulling step has worked by plotting the z-position:
>xmgrace 05_Pull_dist.dat

![Alt text](/figures/moh_pull.png?raw=true "Optional Title")

We can now extract windows with 1A spacing along the z-axis and run windows from each.

If you downloaded the tar file, all outputs from the simulation have been moved into "./md_output" (minus the trajectory files).

# Step 4: Windows
First we need to extract starting points for each window run from the pulling trajectory.  
>./windows directory  

**Important:** We must create an imaged trajectory to extract these windows from in which the bilayer center-of-mass, as defined by N31 head group atoms, is imaged to the origin (0,0,0). This means that when we extract the position of the methanol molecule, we also know that this is the separation between the bilayer COM and the methanol too.

Run cpptraj with image.trajin file:
>trajin 05_Pull_DMPC_MOH.nc  
>center mass origin :2-217@N31  
>vector c0 :1 :1 out c0.out  
>trajout bilayer_zero.nc netcdf  

Then:
>cpptraj DMPC_MOH.prmtop < image.trajin

This should output two files: the imaged trajectory from which we extract the snapshots, and the c0.out file which contains the postion of the methanol at each frame of the trajectory. We also know that this corresponds to the separation between the methanol and bilayer center-of-mass.

We can extract the window starting points using extract_window.py:
>./extract_window.py -i bilayer_zero.nc -p DMPC_MOH.prmtop -d c0.out -start 0 -end 32 -space 1

This will output frames with the methanol at 0, 1, 2, ..., 32A from the bilayer center-of-mass.

Now we can run each window for 30ns using the 06_Prod.in input and run_window_cuda.sh bash run script.  

**Important:** You should run this using a COM_dist.RST file which is a copy of ref_COM_file.RST (i.e. it contains DISTHERE which gets substituted for the correct distance for each window).

>./run_window_cuda.sh

If you have multiple GPUs you may want to split these steps into parallel runs, or run each over a CPU cluster.

If you downloaded the tar file, all outputs from the simulation have been moved into "./md_output" (minus the trajectory files).

# Step 5: Free energy profile
Once the simulations are finished you can build the free energy profile with WHAM.  
>./windows/md_output directory  

The simulations should output a file called "06_Prod_dist.dat" (the name is given in the 06_Prod.in input). This has the format:
> *Frame#*  x:  (*x-coord*)   y:  (*y-coord*)   z:  (*z-coord*)   (*total-coord*)

Where each coord entry is the distance between the methanol and bilayer COM in each dimension. In this tutorial, we are only interested on the z-dimension. In the 06_Prod.in file, the setting to write to this file is istep1=1, so distances are written every single step (0.002 ps) meaning the resulting file can become large. However if possible, it is better to write this data frequently (at least every 2 ps).

For WHAM and the next steps, we only need the z-dimension, so we can use an AWK script to extract this per window:
>awk '{print $1,"",$7}' 06_Prod_dist.dat > prod_dist.dat

This is also possible for every window using the included bash script "fix_dist.sh".

Once you have prod_dist.dat files for every window (format: *Frame#*  *z-dist*), we can run WHAM.

>./windows/wham_run directory  

For wham input, you need a metadata file with the following information:
>*/path/to/file/distance.dat*   *restraint-position*    *force-constant*  
>eg:  
>../md_output/dist_32.0/prod_dist.dat   32.0  5.0  
>../md_output/dist_31.0/prod_dist.dat   31.0  5.0  
> ...etc...

You will notice that the force-constant value in metadata.dat is double that (5 kcal/mol/A^2) compared to that used in the simulations. This is due to differences in how restraints are defined in AMBER vs WHAM. Please see the WHAM documentation for more information.

You can prepare the metadata.dat file using the included script prepare_meta.sh - you may need to update this with the correct paths to your prod_dist.dat files.

Now run WHAM:
>wham 0 32 320 0.00000001 303 0 metadata.dat out.pmf  
>  
>Where the settings are:  
>wham (*start*) (*end*) (*windows*) (*tolerance*) (*temperature*) (*padding*) (*input_metadata*) (*output*)

You can then extract just the PMF curve and plot like so:
>sed '1d' out.pmf | awk '{print $1,"",$2}' > plot_free_energy.dat  
>xmgrace plot_free_energy.dat

You should obtain a plot similar to this:
![Alt text](/figures/plot_free_energy_320.png?raw=true "Optional Title")

To examine how well the overlap is between each window, we can create a histogram of the drug z-position.

>./windows/wham_run/hist_plot directory  

Use the run_hist.sh script to make a histogram from the prod_dist.dat files for each window (this calls the included generate_hist.py). You may need to check the file paths in run_hist.sh.

>./run_hist.sh  

You should get something like this:
>xmgrace hist*dat  
![Alt text](/figures/hist_plot.png?raw=true "Optional Title")

We see that the overlap is suitable when using a 1A separation and 2.5 kcal/mol/A^2 force constant.

#Step 6: Diffusion, resistance and overall permeability
The final step computes first the diffusion along the z-axis, combines the result with the free energy profile data to obtain the resistance along the z-axis and finally integrates the resistance at each z-window to obtain an overall permeability coefficient estimate.

>./windows/wham_run/diffusion directory  

For details on the position-dependent diffusion and resistance calculations please see the following publication from Gerhard Hummer:
http://iopscience.iop.org/article/10.1088/1367-2630/7/1/034/meta

The following methods is based on that used by Carpenter et al (also linked at the top of this tutorial):
http://dx.doi.org/10.1016/j.bpj.2014.06.024

The position-dependent diffusion is calculated as:  

![equation](http://ars.els-cdn.com/content/image/1-s2.0-S000634951400664X-si2.gif)

With 〈Z〉 the average of the reaction coordinate Z, var(Z) the variance of the drug position (the auto-covariance at lag zero) and tau(Z) the characteristic time of the decay of the autocovariance of the drug position Z.

We calculate the autocovarince of the Z-position with increasing lag-time and perform a least-squares-fit to the log of the resulting decay curve to obtain tau(Z). This process is repeated over separate slices of the full trajectory to obtain an average tau(Z) value per window.

If you ran 06_Prod.in for the full 30ns, with istep1=1, then the final output distance file will have 15000000 entries (i.e. a Z-position for every 0.002 ps step).

We use a 1 ns window for the fit, with 1 ns lag. This corresponds to 500000 samples of the Z-position per fit. The script auto_covar.py loads in a prod_dist.dat file, takes the window sample size (500000) and time-step between samples (0.002 ps) plus the option to skip every nth sample. With the -v option you can chose to write out the autocovariance curves (0 off / 1 on). The script then calculates the autocovariance curve per 1 ns window (using 1 ns lag), fits the log of the autocovariance to obtain tau(Z) which is then coverted to the D(Z) value with the above formula. The average D(Z) over all fits is reported (cm^2/s).

Since we have 30 ns of data with 1 ns window, there are a total of 29 fits. You can view each autocovariance curve using the -v 1 option to print these out. An example plot is shown below for the z=32 A window.
>./auto_covar.py -i prod_dist.dat -w 500000 -t 0.002 -skip 0 -v 1  
>xmgrace corr.0.dat

![Alt text](/figures/autocov_32.0.png?raw=true "Optional Title")

*... you may want to kill the auto_covar.py script with CTRL+C as it is very slow when using all samples.*

If you try auto_covar.py using -skip 0 you will notice it is extremely slow. In reality we only need every 10-100 samples. Try using every 10 or every 100 yourself and compare results:
>./auto_covar.py -i prod_dist.dat -w 500000 -t 0.002 -skip 100 -v 0

To obtain diffusion values for every window, you can use the script get_diffusion.sh. Again, you may need to correct the file paths.
>./get_diffusion > all_diffusion_values.out   

**Note:** For windows near z=0, fitting of the autocovariance curves can be problematic. If a tau(Z) value is unrealistically large (above a threshold) this fit is rejected. You may obtain fewer corr.dat files at windows near the bilayer center.

Now that we have the Z-dependent diffusion values D(Z), we can combine these with the value of the free energy at each Z-position to get the local resistance value R(Z) as:  

![equation](http://ars.els-cdn.com/content/image/1-s2.0-S000634951400664X-si5.gif)

Once we have done that calculation we integrate over each R(z) value to get an effective resistance, the inverse of which is the permeability coefficient:  

![equation](http://ars.els-cdn.com/content/image/1-s2.0-S000634951400664X-si4.gif)  

(The water layer is taken as z=0 for this integral).  

I would urge you to do such calculations using a spreadsheet, so that you understand each step. A corresponding spreadsheet is enclosed.

A script to perform each step is also enclosed, called parse_fe_diff.py. This reads in the free energy profile, the diffusion profile and takes the z-limits plus step (i.e. 0->32 A, 1 A step) and the simulation temperature then calculates the resistance and does the integration.  

>./windows/wham_run/overall_perm  directory  

>./parse_fe_diff.py -fe ../plot.dat -diff ../diffusion/all_diffusion_values.out -start 0 -end 32 -space 1 -temp 303  

This will output the free energy curve (free_energy_profile.parse.dat), the diffusion curve (diffusion_profile.parse.dat) and the resistance profile (resistance_profile.parse.dat) plus the overall permeability coefficient.

Finally, we have only done the calculations for a single monolayer (water phase into the membrane center). If wish to get the values to move all the way through a symmetric membrane we can assume the values will be the same on the opposite side of the bilayer due to symmetry.

>./windows/wham_run/overall_perm/full_profile_perm  directory  
>tac ../free_energy_profile.parse.dat | awk '{print $1\*-1,"",$2}' > tmp  
>cat tmp ../free_energy_profile.parse.dat > full_fe.dat  
>rm tmp  
>tac ../../diffusion/all_diffusion_values.out | awk '{print $1\*-1,"",$2}' > tmp  
>cat ../../diffusion/all_diffusion_values.out tmp > full_diffusion.dat  
>rm tmp  

>./parse_fe_diff.py -fe full_fe.dat -diff full_diffusion.dat -start -32 -end 32 -space 1 -temp 303  

Will output the result for the full bilayer.  

The resulting free energy profile:  

![Alt text](/figures/free_energy_full.png?raw=true "Optional Title")  

The diffusion profile:  

![Alt text](/figures/diffusion_full.png?raw=true "Optional Title")  

The resistance profile:  

![Alt text](/figures/resistance_full.png?raw=true "Optional Title")  

The values I obtain using 30 ns windows are:

G(pen): 3.27 kcal/mol (free energy at the center z=0)  
P(eff): 0.159 cm/s

Your values should be somewhere in this ballpark.

These compare favourably with those obtained by Orsi et al (also linked at the top of this tutorial):
http://pubs.acs.org/doi/abs/10.1021/jp903248s

G(pen): ~3.3 kcal/mol  
P(eff): 0.18 ± 0.2 cm/s

Finally, there have been a number of articles addressing the issue of obtaining converged PMF profiles which you should take note of. Try to extend window simulation time and perform as many independent repeats from different initial coordinates and velocities to be sure your profiles are converged.

A few papers you may want to read on the issues of convergence are linked below:

http://pubs.acs.org/doi/abs/10.1021/ct2009208  
http://pubs.acs.org/doi/abs/10.1021/ct200316w

If you use the AMBER method and lipid force-field to generate PMFs for publication, please cite the relevant AMBER and Lipid14/Lipid16 references:  

http://pubs.acs.org/doi/abs/10.1021/ct4010307
