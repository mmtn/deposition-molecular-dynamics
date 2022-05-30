from enum import Enum


class DirectoriesEnum(Enum):
    """Map strings to directory paths"""

    FAILED = "failed"
    SUCCESS = "iterations"
    WORKING = "current"


class SettingsEnum(Enum):
    """Map strings to settings variables"""

    COMMAND_PREFIX = "command_prefix"
    DEPOSITION_ELEMENT = "deposition_element"
    DEPOSITION_HEIGHT = "deposition_height_Angstroms"
    DEPOSITION_TEMPERATURE = "deposition_temperature_Kelvin"
    DEPOSITION_TIME = "deposition_time_picoseconds"
    DEPOSITION_TYPE = "deposition_type"
    DRIVER_SETTINGS = "driver_settings"
    LOG_FILENAME = "log_filename"
    MAX_SEQUENTIAL_FAILURES = "max_sequential_failures"
    MAX_TOTAL_ITERATIONS = "max_total_iterations"
    MIN_VELOCITY = "min_velocity_metres_per_second"
    MOLECULE_XYZ_FILE = "molecule_xyz_file"
    NUM_DEPOSITED_PER_ITERATION = "num_deposited_per_iteration"
    POSITION_DISTRIBUTION = "position_distribution"
    POSITION_DISTRIBUTION_PARAMS = "position_distribution_parameters"
    POSTPROCESSING = "postprocessing"
    RELAXATION_TIME = "relaxation_time_picoseconds"
    SIMULATION_CELL = "simulation_cell"
    STRICT_POSTPROCESSING = "strict_postprocessing"
    SUBSTRATE_XYZ_FILE = "substrate_xyz_file"
    VELOCITY_DISTRIBUTION = "velocity_distribution"
    VELOCITY_DISTRIBUTION_PARAMS = "velocity_distribution_parameters"


class SimulationCellEnum(Enum):
    """Map strings to simulation cell parameters"""

    A = "a"
    B = "b"
    C = "c"
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


class StateEnum(Enum):
    """Map strings to simulation state information"""

    COORDINATES = "state"
    ELEMENTS = "elements"
    VELOCITIES = "velocities"


class StatusEnum(Enum):
    """Map strings to status information"""

    ITERATION_NUMBER = "iteration_number"
    LAST_UPDATED = "last_updated"
    PICKLE_LOCATION = "pickle_location"
    SEQUENTIAL_FAILURES = "sequential_failures"
    TOTAL_FAILURES = "total_failures"
