.. _drivers:


Molecular dynamics drivers
==========================

The function of the driver classes is to interface between this package and the molecular dynamics software which is
doing the calculation. This package currently provides drivers for :doc:`GULP <GULPDriver>` and
:doc:`LAMMPS <LAMMPSDriver>` which should work for most cases straight out of the box. See the individual driver
documentation for information about additional settings and configuration.

If you are interested in writing your own driver for a different piece of software see
:doc:`here <new_drivers>`.


Additional documentation
------------------------

.. toctree::
   :maxdepth: 1

   GULPDriver
   LAMMPSDriver
   new_drivers


External links
--------------

- `GULP website <http://gulp.curtin.edu.au/gulp/>`_
- `LAMMPS website <https://www.lammps.org/>`_
