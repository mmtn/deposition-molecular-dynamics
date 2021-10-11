import os

from schema import And, Optional, Or, Schema, Use

from deposition.schema_validation import allowed_deposition_type, strictly_positive


def settings_schema():
    """
    A list of the required and optional settings for the simulation. These settings control the type and nature of the
    deposition to be simulated.

    Note that settings for the :meth:`simulation cell <deposition.schema_definitions.simulation_cell_schema>` and
    molecular dynamics :ref:`driver <drivers>` must also be provided.

    List of required settings:

    - deposition_type (required, `string`)
        - the style of deposition to perform, may activate conditionally required settings (see below)
        - available options: 'monatomic', 'diatomic', 'molecule'
    - deposition_height_Angstroms (required, `int` or `float`)
        - how far above the surface to add new atoms/molecules
    - deposition_temperature_Kelvin (required, `int` or `float`)
        - temperature of newly added atoms/molecules
    - minimum_deposition_velocity_metres_per_second (required, `int` or `float`)
        - set a minimum velocity for added atoms/molecules
    - relaxation_time_picoseconds (required, `int` or `float`)
        - duration to simulate the system before the deposition event
    - deposition_time_picoseconds (required, `int` or `float`)
        - duration of the deposition event to allow for bonding to the surface
    - bonding_distance_cutoff_Angstroms (required, `int` or `float`)
        - minimum separation for two atoms to be considered bonded
    - num_deposited_per_iteration (required, `int`)
        - number of atoms/molecules added in each iteration
    - maximum_sequential_failures (required, `int`)
        - number of failed iterations before the calculation is terminated
    - maximum_total_iterations (required, `int`)
        - total number of iterations to run before exiting
    - substrate_xyz_file (required, `path`)
        - path to an XYZ file of the initial substrate structures

    Required settings (additional sections):

    - driver_settings (required, `dict`)
        - settings for the :ref:`molecular dynamics driver <drivers>`
    - simulation_cell (required, `dict`)
        - specification of the :meth:`simulation cell <deposition.schema_definitions.simulation_cell_schema>`

    Conditionally required settings:

    - deposition_element (required for 'monatomic' or 'diatomic' deposition, `string`)
        - symbol of the element to be deposited
    - diatomic_bond_length_Angstroms (required for 'diatomic' deposition, `int` or `float`):
        - diatomic bond length
    - molecule_xyz_file (required for 'molecule' deposition, `path`):
        - path to the structure of the molecule to be deposited

    Optional settings:

    - log_filename (optional, `path`, default="deposition.log")
        - path to use for the log file
    - command_prefix (optional, `string` default="")
        - prefix to the shell command when calling the molecular dynamics software, e.g. mpiexec

    """
    return Schema({
        "deposition_type": And(str, Use(allowed_deposition_type)),
        "deposition_height_Angstroms": And(Or(int, float), Use(strictly_positive)),
        "deposition_temperature_Kelvin": And(Or(int, float), Use(strictly_positive)),
        "minimum_deposition_velocity_metres_per_second": And(Or(int, float), Use(strictly_positive)),
        "relaxation_time_picoseconds": And(Or(int, float), Use(strictly_positive)),
        "deposition_time_picoseconds": And(Or(int, float), Use(strictly_positive)),
        "bonding_distance_cutoff_Angstroms": And(Or(int, float), Use(strictly_positive)),
        "num_deposited_per_iteration": And(int, Use(strictly_positive)),
        "maximum_sequential_failures": And(int, Use(strictly_positive)),
        "maximum_total_iterations": And(int, Use(strictly_positive)),
        "driver_settings": dict,
        "simulation_cell": dict,
        "substrate_xyz_file": os.path.exists,
        Optional("log_filename", default="deposition.log"): str,
        Optional("command_prefix", default=""): str,
        Optional("deposition_element"): str,
        Optional("diatomic_bond_length_Angstroms"): And(Or(int, float), Use(strictly_positive)),
        Optional("molecule_xyz_file"): os.path.exists,
    })


def simulation_cell_schema():
    """
    Input schema for the parameters which define the periodic cell. Lengths are in Angstroms and angles are in degrees.

    Example::

        a: 24  # Angstroms
        b: 24  # Angstroms
        c: 200  # Angstroms
        alpha: 90  # degrees
        beta: 90  # degrees
        gamma: 90  # degrees
    """
    return Schema({
        "a": And(Or(int, float), Use(strictly_positive)),
        "b": And(Or(int, float), Use(strictly_positive)),
        "c": And(Or(int, float), Use(strictly_positive)),
        "alpha": And(Or(int, float), Use(strictly_positive)),
        "beta": And(Or(int, float), Use(strictly_positive)),
        "gamma": And(Or(int, float), Use(strictly_positive))
    })
