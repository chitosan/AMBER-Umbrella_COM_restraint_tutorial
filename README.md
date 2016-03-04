# AMBER-Umbrella_COM_restraint_tutorial
Tutorial to run AMBER umbrella COM restraint code and derive free energy of transfer profile for methanol through DMPC membrane.

# Requirements:

* AMBER16 or above (has COM umbrella restraint code)
* Python 2.7 (https://www.continuum.io/downloads)
* WHAM (http://membrane.urmc.rochester.edu/content/wham)

# Introduction
This tutorial uses the AMBER16 center-of-mass (COM) umbrella restraint code to determine the free energy of transfer profile for a methanol molecule through a DMPC membrane bilayer. The methanol molecule is first pulled from the center of the membrane out into the water phase. From the pulling step, we extract starting positions with methanol at 0, 1, 2, ..., 32 A from the membrane center. We run windows with methanol restrained at each of these positions. From the fluctuation in the z-position, we can construct the free energy profile using WHAM. Finally, we use the same information to derive the z-diffusion and z-resistance profiles and overall permeability coefficient.

There is a great deal of literature available on running z-restraint simulations which I would encourage you to consult. A few examples include:

http://pubs.acs.org/doi/abs/10.1021/jp035260s

http://pubs.acs.org/doi/abs/10.1021/jp903248s

http://dx.doi.org/10.1016/j.bpj.2014.06.024

# Step 1: Parameters
First we need starting membrane bilayer PDB file and coordinates and parameters for methanol.

You can follow the AMBER tutorial TUTORIAL A16: An Amber Lipid Force Field Tutorial: Lipid14 to obtain an equilibrated lipid bilayer.

Use antechamber to create AMBER parameters for methanol:

>antechamber -i methanol.pdb -fi pdb -o MOH.mol2 -fo mol2 -c bcc -s 2

Then use tleap to convert the resulting MOH.mol2 into MOH.off:

>tleap -f convert.leap

# Step 2: Placement
Next we place the methanol molecule at the center of the membrane (z-distance between methanol and DMPC bilayer is zero).

A study has shown that pulling from the middle of the membrane out allows faster convergence of PMFs rather than pulling from the water phase into the membrane:

http://pubs.acs.org/doi/abs/10.1021/jp501622d

You can use the python script to place the methanol molecule at z=0 from the DMPC bilayer COM:

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

>parmed.py -i details_parmed.in

You will see that the N31 atom index values corresponds to those in ref_COM_file.RST

Please go through the AMBER manual so that you know what each line in the ref_COM_file.RST means. Important flags are:
>rk2=2.5    *restraint force constant*  
>fxyz=0,0,1 *turn on umbrella COM in z-direction only*  
>outxyz=1   *print position of restrained molecule in x,y,z dimensions*

You may notice that ref_COM_file.RST has settings "DISTHERE" - we will copy this to a new file and add in the correct settings here.
>cp ref_COM_file.RST COM_dist.RST

Change DISTHERE to 0.0 in COM_dist.RST. 

We also need a file for the pulling step COM_pull.RST. This is similar yet specifies a starting positon of 0 and a final position of 32, the force constant for pulling is also reduced to 1.1.

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

# Step 4: Windows
First we need to extract starting points for each window run from the pulling trajectory.

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

>./run_window_cuda.sh

If you have multiple GPUs you may want to split these steps into parallel runs, or run each over a CPU cluster.

# Step 5: Free energy profile
Once the simulations are finished you can build the free energy profile with WHAM.

The simulations should output a file called "06_Prod_dist.dat" (the name is given in the 06_Prod.in input). This has the format:
> Frame#  x:  (*x-coord*)   y:  (*y-coord*)   z:  (*z-coord*)   (*total-coord*)

Where each coord entry is the distance between the methanol and bilayer COM in each dimension. In this tutorial, we are only interested on the z-dimension. In the 06_Prod.in file, the setting to write to this file is istep1=1, so distances are written every single step (0.002ps) meaning the resulting file can become large. However if possible, it is better to write this data.

For WHAM and the next steps, we only need the z-dimension, so we can use an AWK script to extract this per window:
>awk '{print $1,"",$7}' 06_Prod_dist.dat > prod_dist.dat

This is also possible for every window using the included bash script "fix_dist.sh".

Once you have prod_dist.dat files for every window (format: *Frame#*  *z-dist*), we can run WHAM.

For wham input, you need a metadata file with the following information:
>*/path/to/file/distance.dat*   *restraint-position*    *force-constant*  
>eg:  
>../md_output/dist_32.0/prod_dist.dat   32.0  5.0  
>../md_output/dist_31.0/prod_dist.dat   31.0  5.0  
> ...etc...

You will notice that the force-constant value in metadata.dat is double that (5 kcal/mol/A) compared to that used in the simulations. This is due to differences in how restraints are defined in AMBER vs WHAM. Please see the WHAM documentation for more information.

You can prepare the metadata.dat file using the included script prepare_meta.sh - you may need to update this with the correct paths to your prod_dist.dat files.

Now run WHAM:
>wham 0 32 160 0.00000001 303 0 metadata.dat out.pmf  
>  
>Where the settings are:  
>wham (*start*) (*end*) (*windows*) (*tolerance*) (*temperature*) (*padding*) (*input_metadata*) (*output*)

You can then extract just the PMF curve and plot like so:
>sed '1d' out.pmf | awk '{print $1,"",$2}' > plot_free_energy.dat  
>xmgrace plot_free_energy.dat
