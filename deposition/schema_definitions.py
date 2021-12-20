import os

from schema import And, Optional, Or, Schema, Use

from deposition import schema_validation
from deposition.enums import SettingsEnum, SimulationCellEnum

settings_schema = Schema(
    {
        SettingsEnum.BONDING_DISTANCE_CUTOFF.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.DEPOSITION_HEIGHT.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.DEPOSITION_TEMPERATURE.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.DEPOSITION_TIME.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.DEPOSITION_TYPE.value: And(
            str, Use(schema_validation.allowed_deposition_types)
        ),
        SettingsEnum.MAX_SEQUENTIAL_FAILURES.value: And(
            int, Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.MAX_TOTAL_ITERATIONS.value: And(
            int, Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.MIN_VELOCITY.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.NUM_DEPOSITED_PER_ITERATION.value: And(
            int, Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.POSITION_DISTRIBUTION.value: And(
            str, Use(schema_validation.allowed_position_distributions)
        ),
        SettingsEnum.RELAXATION_TIME.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SettingsEnum.DRIVER_SETTINGS.value: dict,
        SettingsEnum.SIMULATION_CELL.value: dict,
        SettingsEnum.SUBSTRATE_XYZ_FILE.value: os.path.exists,
        SettingsEnum.VELOCITY_DISTRIBUTION.value: And(
            str, Use(schema_validation.allowed_velocity_distributions)
        ),
        Optional(SettingsEnum.COMMAND_PREFIX.value, default=""): str,
        Optional(SettingsEnum.DEPOSITION_ELEMENT.value, default=None): str,
        Optional(SettingsEnum.LOG_FILENAME.value, default="deposition.log"): str,
        Optional(SettingsEnum.MOLECULE_XYZ_FILE.value, default=None): os.path.exists,
        Optional(SettingsEnum.POSITION_DISTRIBUTION_PARAMS.value, default=[]): list,
        Optional(SettingsEnum.POSTPROCESSING.value, default=None): dict,
        Optional(SettingsEnum.STRICT_STRUCTURAL_ANALYSIS.value, default=False): bool,
        Optional(
            SettingsEnum.TO_ORIGIN_BEFORE_EACH_ITERATION.value, default=False
        ): bool,
        Optional(SettingsEnum.VELOCITY_DISTRIBUTION_PARAMS.value, default=[]): list,
    }
)

simulation_cell_schema = Schema(
    {
        SimulationCellEnum.A.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SimulationCellEnum.B.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SimulationCellEnum.C.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SimulationCellEnum.ALPHA.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SimulationCellEnum.BETA.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
        SimulationCellEnum.GAMMA.value: And(
            Or(int, float), Use(schema_validation.strictly_positive)
        ),
    }
)


def get_settings_schema():
    """
    A list of the required and optional settings for the simulation. These settings control the type and nature of the
    deposition to be simulated.

    Note that settings for the :meth:`simulation cell <deposition.schema_definitions.simulation_cell_schema>` and
    molecular dynamics :ref:`driver <drivers>` must also be provided.

    List of required settings:

    - deposition_type (required, `str`)
        - the style of deposition to perform, may activate conditionally required settings (see below)
        - available options: 'monatomic', 'diatomic', 'molecule'
    - deposition_height_Angstroms (required, `int` or `float`)
        - how far above the surface to add new atoms/molecules
    - deposition_temperature_Kelvin (required, `int` or `float`)
        - temperature of newly added atoms/molecules
    - velocity_distribution (required, `str`)
        - name of the method for generating new velocities
    - velocity_distribution_parameters (list)
        - settings for the given velocity distribution
    - position_distribution (required, `str`)
        - name of the method for generating new positions
    - position_distribution_parameters (list)
        - settings for the given position distribution
    - relaxation_time_picoseconds (required, `int` or `float`)
        - duration to simulate the system before the deposition event
    - deposition_time_picoseconds (required, `int` or `float`)
        - duration of the deposition event to allow for bonding to the surface
    - bonding_distance_cutoff_Angstroms (required, `int` or `float`)
        - minimum separation for two atoms to be considered bonded
    - num_deposited_per_iteration (required, `int`)
        - number of atoms/molecules added in each iteration
    - max_sequential_failures (required, `int`)
        - number of failed iterations before the calculation is terminated
    - max_total_iterations (required, `int`)
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
    - to_origin_before_each_iteration (optional, `bool`, default=False):
        - relocates the structure to the origin before each iteration to prevent migration from depositing on top
    - strict_structural_analysis (optional, `bool`, default=False)
        - raises an error instead of a warning if the structural analysis fails
    """
    return settings_schema


def get_simulation_cell_schema():
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
    return get_simulation_cell_schema
