import os
from schema import Schema, And, Or, Use, Optional

from deposition.schema_validation import strictly_positive, allowed_deposition_type

"""
# settings.yaml

Paths can be relative or absolute.

"""
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
    "log_filename": str,
    Optional("command_prefix", default=""): str,
    Optional("diatomic_bond_length_Angstroms"): And(Or(int, float), Use(strictly_positive)),
})


"""
# Input schema for simulation cell parameters

Defines the periodic cell. Lengths are in Angstroms. Angles are in degrees

Example
    a: 24  # Angstroms
    b: 24  # Angstroms
    c: 200  # Angstroms
    alpha: 90  # degrees
    beta: 90  # degrees
    gamma: 90  # degrees

"""
simulation_cell_schema = Schema({
    "a": And(Or(int, float), Use(strictly_positive)),
    "b": And(Or(int, float), Use(strictly_positive)),
    "c": And(Or(int, float), Use(strictly_positive)),
    "alpha": And(Or(int, float), Use(strictly_positive)),
    "beta": And(Or(int, float), Use(strictly_positive)),
    "gamma": And(Or(int, float), Use(strictly_positive))
})
