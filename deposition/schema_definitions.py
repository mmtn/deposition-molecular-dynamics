import os
from schema import Schema, And, Or, Use, Optional

from deposition.schema_validation import strictly_positive, allowed_deposition_type

settings_schema = Schema({
    "deposition_type": And(str, Use(allowed_deposition_type)),
    "deposition_element": str,
    "deposition_height_Angstroms": And(Or(int, float), Use(strictly_positive)),
    "deposition_temperature_Kelvin": And(Or(int, float), Use(strictly_positive)),
    "minimum_deposition_velocity_metres_per_second": And(Or(int, float), Use(strictly_positive)),
    "relaxation_time_picoseconds": And(Or(int, float), Use(strictly_positive)),
    "deposition_time_picoseconds": And(Or(int, float), Use(strictly_positive)),
    "bonding_distance_cutoff_Angstroms": And(Or(int, float), Use(strictly_positive)),
    "num_deposited_per_iteration": And(int, Use(strictly_positive)),
    "maximum_sequential_failures": And(int, Use(strictly_positive)),
    "maximum_total_iterations": And(int, Use(strictly_positive)),
    "driver_settings": Or(dict, os.path.exists),
    "simulation_cell": Or(dict, os.path.exists),
    "substrate_xyz_file": os.path.exists,
    Optional("log_filename", default="deposition.log"): str,
    Optional("command_prefix", default=""): str,
    Optional("diatomic_bond_length_Angstroms"): And(Or(int, float), Use(strictly_positive)),
})
"""
Input schema for simulation settings. Note that paths can be relative or absolute.

More information about:

* 

Schema:

* deposition_type: can currently be set to either 'monatomic' or 'diatomic'
* deposition_element: symbol of the element to be deposited
* deposition_height_Angstroms: how far above the surface to add new atoms/molecules
* deposition_temperature_Kelvin: temperature of newly added atoms/molecules
* minimum_deposition_velocity_metres_per_second: set a minimum velocity for added atoms/molecules
* relaxation_time_picoseconds: duration to simulate the system before the deposition event
* deposition_time_picoseconds: duration of the deposition event to allow for bonding to the surface
* bonding_distance_cutoff_Angstroms: minimum separation for two atoms to be considered bonded
* num_deposited_per_iteration: number of atoms/molecules added in each iteration
* maximum_sequential_failures: number of failed iterations before the calculation is terminated
* maximum_total_iterations: total number of iterations to run the calculation for
* driver_settings: settings for the :ref:`molecular dynamics drivers <drivers>`
* simulation_cell: specification of the :meth:`simulation cell <deposition.schema_definitions.simulation_cell_schema>`
* substrate_xyz_file: path to an XYZ file of the initial substrate to deposit on
* log_filename (optional, default="deposition.log"): path to use for the log file
* command_prefix (optional, default=""): prefix to the simulation command, e.g. mpiexec
* diatomic_bond_length_Angstroms (only required for diatomic deposition): diatomic bond length

:meta hide-value:
"""

simulation_cell_schema = Schema({
    "a": And(Or(int, float), Use(strictly_positive)),
    "b": And(Or(int, float), Use(strictly_positive)),
    "c": And(Or(int, float), Use(strictly_positive)),
    "alpha": And(Or(int, float), Use(strictly_positive)),
    "beta": And(Or(int, float), Use(strictly_positive)),
    "gamma": And(Or(int, float), Use(strictly_positive))
})
"""
Input schema for the parameters which define the periodic cell. Lengths are in Angstroms and angles are in degrees. 

Example::

    a: 24  # Angstroms
    b: 24  # Angstroms
    c: 200  # Angstroms
    alpha: 90  # degrees
    beta: 90  # degrees
    gamma: 90  # degrees

:meta hide-value:
"""