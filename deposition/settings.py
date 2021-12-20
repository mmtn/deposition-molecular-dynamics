from deposition import distributions, schema_validation
from deposition.enums import SettingsEnum


class Settings:
    """Class to hold all settings for the deposition calculation"""

    def __init__(self, settings):
        self.bonding_distance_cutoff = settings[
            SettingsEnum.BONDING_DISTANCE_CUTOFF.value
        ]
        self.command_prefix = settings[SettingsEnum.COMMAND_PREFIX.value]
        self.deposition_element = settings[SettingsEnum.DEPOSITION_ELEMENT.value]
        self.deposition_height = settings[SettingsEnum.DEPOSITION_HEIGHT.value]
        self.deposition_temperature = settings[
            SettingsEnum.DEPOSITION_TEMPERATURE.value
        ]
        self.deposition_time = settings[SettingsEnum.DEPOSITION_TIME.value]
        self.deposition_type = settings[SettingsEnum.DEPOSITION_TYPE.value]
        self.driver_settings = settings[SettingsEnum.DRIVER_SETTINGS.value]
        self.log_filename = settings[SettingsEnum.LOG_FILENAME.value]
        self.max_sequential_failures = settings[
            SettingsEnum.MAX_SEQUENTIAL_FAILURES.value
        ]
        self.max_total_iterations = settings[SettingsEnum.MAX_TOTAL_ITERATIONS.value]
        self.min_velocity = settings[SettingsEnum.MIN_VELOCITY.value]
        self.molecule_xyz_file = settings[SettingsEnum.MOLECULE_XYZ_FILE.value]
        self.num_deposited_per_iteration = settings[
            SettingsEnum.NUM_DEPOSITED_PER_ITERATION.value
        ]
        self.position_distribution = settings[SettingsEnum.POSITION_DISTRIBUTION.value]
        self.position_distribution_parameters = settings[
            SettingsEnum.POSITION_DISTRIBUTION_PARAMS.value
        ]
        self.relaxation_time = settings[SettingsEnum.RELAXATION_TIME.value]
        self.simulation_cell = settings[SettingsEnum.SIMULATION_CELL.value]
        self.strict_structural_analysis = settings[
            SettingsEnum.STRICT_STRUCTURAL_ANALYSIS.value
        ]
        self.substrate_xyz_file = settings[SettingsEnum.SUBSTRATE_XYZ_FILE.value]
        self.to_origin_before_each_iteration = settings[
            SettingsEnum.TO_ORIGIN_BEFORE_EACH_ITERATION.value
        ]
        self.velocity_distribution = settings[SettingsEnum.VELOCITY_DISTRIBUTION.value]
        self.velocity_distribution_parameters = settings[
            SettingsEnum.VELOCITY_DISTRIBUTION_PARAMS.value
        ]
        self.validate(settings)

    def validate(self, settings):
        """
        Args:
            settings:
        """
        # check that required options for the deposition type are present
        print(self.deposition_type)
        for requirement in schema_validation.DEPOSITION_TYPES[self.deposition_type]:
            assert (
                requirement in settings.keys()
            ), f"{requirement} required in {self.deposition_type} deposition"

        # check that the position distribution is valid and has the correct number of arguments
        position_distribution = distributions.get_position_distribution(
            self.position_distribution,
            self.position_distribution_parameters,
            None,
            0.0,
        )

        # check that the velocity distribution is valid and has the correct number of arguments
        velocity_distribution = distributions.get_velocity_distribution(
            self.velocity_distribution,
            self.velocity_distribution_parameters,
        )
