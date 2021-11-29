.. _drivers:


Molecular dynamics drivers
==========================

The function of the driver classes is to interface between this package and the molecular dynamics software which is
doing the calculation. This package currently provides drivers for :doc:`GULP <GULPDriver>` and
:doc:`LAMMPS <LAMMPSDriver>` which should work for most cases straight out of the box. See the individual driver
documentation for information about additional settings and configuration.

If you are interested in writing your own driver for a different piece of software see
:doc:`here <new_drivers>`.

The following settings are required for all drivers:

- `name` (str): name of the molecular dynamics software
- `path_to_binary` (path): path to the binary of the molecular dynamics software
- `path_to_input_template` (path): path to the input template
- `velocity_scaling_from_metres_per_second` (int/float): scaling value to convert from the internal units of the
  software to SI units, e.g. scale by 0.00001 to convert from Angstroms per femtosecond to metres per second


Additional documentation
------------------------

.. toctree::
   :maxdepth: 1

   GULPDriver
   LAMMPSDriver
   TemplateDriver
   MolecularDynamicsDriver
   new_drivers


External links
--------------

- `GULP website <http://gulp.curtin.edu.au/gulp/>`_
- `LAMMPS website <https://www.lammps.org/>`_
