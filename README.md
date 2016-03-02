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
