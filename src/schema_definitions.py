import os
from src.schema_validation import strictly_positive, allowed_deposition_types
from schema import Schema, And, Or, Use, Optional


"""
# simulation_cell.yaml example

Define the periodic cell. 
Length units are Angstrom. 
Angle units are degrees.

    a: 24
    b: 24
    c: 200
    alpha: 90
    beta: 90
    gamma: 90

"""
simulation_cell_schema = Schema({
    "a": And(Or(int, float), Use(strictly_positive)),
    "alpha": And(Or(int, float), Use(strictly_positive)),
    "b": And(Or(int, float), Use(strictly_positive)),
    "beta": And(Or(int, float), Use(strictly_positive)),
    "c": And(Or(int, float), Use(strictly_positive)),
    "gamma": And(Or(int, float), Use(strictly_positive))
})


"""
# settings.yaml example

For depositing oxygen on an aluminium substrate at 300 K. 
Paths can be relative or absolute.
All length units are Angstroms.
    
    # paths to additional settings
    driver_settings: settings/lammps_settings.yaml
    simulation_cell_data: settings/aluminium_100_6x6x6_simulation_cell.yaml
    substrate_xyz_file: settings/aluminium_100_6x6x6_substrate.xyz
    
    # deposition settings (physics)
    deposition_type: monatomic
    deposition_element: O
    deposition_height_Angstroms: 16
    deposition_temperature_Kelvin: 300
    minimum_deposition_velocity_metres_per_second: 32
    
    # deposition settings (numeric)
    bonding_distance_cutoff_Angstroms: 4
    num_deposited_per_iteration: 1
    maximum_total_iterations: 10
    maximum_sequential_failures: 5
    
"""
settings_schema = Schema({
    "deposition_element": str,
    "deposition_height_Angstroms": And(Or(int, float), Use(strictly_positive)),
    "deposition_temperature_Kelvin": And(Or(int, float), Use(strictly_positive)),
    "deposition_type": And(str, Use(allowed_deposition_types)),
    "driver_settings": os.path.exists,
    "maximum_sequential_failures": And(int, Use(strictly_positive)),
    "maximum_total_iterations": And(int, Use(strictly_positive)),
    "minimum_deposition_velocity_metres_per_second": And(Or(int, float), Use(strictly_positive)),
    "num_deposited_per_iteration": And(int, Use(strictly_positive)),
    "simulation_cell_data": os.path.exists,
    "substrate_xyz_file": os.path.exists,
    Optional("bonding_distance_cutoff_Angstroms"): And(Or(int, float), Use(strictly_positive)),
    Optional("command_prefix", default=""): str,
    Optional("diatomic_bond_length_Angstroms"): And(Or(int, float), Use(strictly_positive)),
})

