# AMBER-Umbrella_COM_restraint_tutorial
Tutorial to run AMBER umbrella COM restraint code and derive free energy of transfer profile for methanol through DMPC membrane.

# Requirements:
  AMBER16 or above (has COM umbrella restraint code)

  Linux / bash scripts

  Python 2.7 (https://www.continuum.io/downloads)
  
  WHAM (http://membrane.urmc.rochester.edu/content/wham)

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

Please go through the AMBER manual so that you know what each line in the ref_COM_file.RST means. Important flags are:
>rk2=2.5    *restraint force constant*
>fxyz=0,0,1 *turn on umbrella COM in z-direction only*  
>outxyz=1   *print position of restrained molecule in x,y,z dimensions*

You may notice that ref_COM_file.RST has settings "DISTHERE" - we will copy this to a new file and add in the correct settings here.
>cp ref_COM_file.RST COM_dist.RST

Change DISTHERE to 0.0 in COM_dist.RST. 

We also need a file for the pulling step. This is similar yet specifies a starting positon of 0 and a final position of 32, the force constant for pulling is also reduced to 1.1.
