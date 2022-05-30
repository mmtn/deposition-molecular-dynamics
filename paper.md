---
title: 'DepositionMD: a molecular dynamics wrapper for modelling deposition processes'
tags:
  - Python
  - physics
  - molecular dynamics
  - computational physics
  - LAMMPS
  - oxidation
authors:
  - name: M. J. Cyster
    orcid: 0000-0003-0872-7098
    affiliation: 1
  - name: J. S. Smith
    affiliation: 1
  - name: S. P. Russo
    affiliation: 1
  - name: J. H. Cole
    affiliation: 1
affiliations:
 - name: Chemical and Quantum Physics, School of Science, RMIT University, Melbourne, Australia
   index: 1
date: 9 May 2022
bibliography: paper.bib

---

# Summary

Molecular dynamics (MD) is a powerful tool for simulating the motion of particles in a wide range of systems. Starting from the initial coordinates and velocities, the evolution of the system is determined by solving the equations of motion subject to an interatomic force field. While many software tools are available to solve molecular dynamics problems, they are predominantly limited to a fixed number of particles for each simulation. In processes such as oxidation, chemical vapour deposition, or other surface deposition techniques, the addition of new particles to the ongoing calculation is an essential part of understanding the chemical and physical interactions which take place.

# Statement of need

`DepositionMD` is a Python package for simulating deposition-like processes. Starting from initial coordinates, the package constructs input files for the chosen MD software which include one or more new atoms or molecules and runs the simulation. Following this the output is assessed to determine the success or failure of the deposition event. Upon a successful deposition the final state of this simulation is taken as the initial state for the next simulation where more new atoms (or molecules) are added. Otherwise the failed deposition is saved and the next simulation started from the most recent successful deposition.

`DepositionMD` provides classes which interface with the popular MD packages `GULP` [@Gale:2003] and `LAMMPS` [@LAMMPS] but can be integrated with any MD software by writing a Python class with methods to write input files and read data from the output files. The functional forms of the spatial and velocity distributions used for the deposited atoms or molecules can also be implemented by the user. Lastly, the user is able to construct customised routines which assess the success or failure of each event. 

Originally developed to study the oxidation of aluminium substrates [@Cyster:2021], the package is flexible and extensible. Simulating the deposition of any material on to any substrate is possible provided appropriate force field models are available which work with the molecular dynamics software. `DepositionMD` is a tool with a simple interface but a range of powerful options which allows researchers to focus on studying deposition phenomena without manually managing each of the many MD simulations required.

# Acknowledgements

The authors acknowledge support of the Australian Research Council through grants DP140100375, CE170100026 (M.J.C.), and CE170100039 (J.S.S.). This research was undertaken with the assistance of resources from the National Computational Infrastructure (NCI), which is supported by the Australian Government. The authors acknowledge the people of the Woi wurrung and Boon wurrung language groups of the eastern Kulin Nations on whose unceded lands we work. We also acknowledge the Ngunnawal people, the Traditional Custodians of the Australian Capital Territory where NCI is located. We respectfully acknowledge the Traditional Custodians of the lands and waters across Australia and their Elders: past, present, and emerging.

# References

