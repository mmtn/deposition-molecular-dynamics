import os
from schema import Schema, And, Or, Use, Optional, SchemaError

ALLOWED_DEPOSITION_TYPES = ("monatomic", "diatomic")


def deposition_type_validation(deposition_type):
    if deposition_type in ALLOWED_DEPOSITION_TYPES:
        return deposition_type
    else:
        raise SchemaError(f"deposition type must be one of: {ALLOWED_DEPOSITION_TYPES}")


def strictly_positive(number):
    if number <= 0:
        raise SchemaError("value must be greater than zero")
    return number


def reserved_keyword(value):
    raise SchemaError("this key is reserved for internal use")


simulation_cell_schema = Schema({
    "a": And(Or(int, float), Use(strictly_positive)),
    "alpha": And(Or(int, float), Use(strictly_positive)),
    "b": And(Or(int, float), Use(strictly_positive)),
    "beta": And(Or(int, float), Use(strictly_positive)),
    "c": And(Or(int, float), Use(strictly_positive)),
    "gamma": And(Or(int, float), Use(strictly_positive))
})

settings_schema = Schema({
    "deposition_element": str,
    "deposition_height_Angstroms": And(Or(int, float), Use(strictly_positive)),
    "deposition_temperature_Kelvin": And(Or(int, float), Use(strictly_positive)),
    "deposition_type": And(str, Use(deposition_type_validation)),
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
