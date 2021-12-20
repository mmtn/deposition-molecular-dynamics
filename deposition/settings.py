from deposition import distributions, postprocessing, schema_validation
from deposition.enums import SettingsEnum


class Settings:
    """Class to hold all settings for the deposition calculation"""

    def __init__(self, settings):
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
        self.postprocessing = settings[SettingsEnum.POSTPROCESSING.value]
        self.relaxation_time = settings[SettingsEnum.RELAXATION_TIME.value]
        self.simulation_cell = settings[SettingsEnum.SIMULATION_CELL.value]
        self.strict_structural_analysis = settings[
            SettingsEnum.STRICT_STRUCTURAL_ANALYSIS.value
        ]
        self.substrate_xyz_file = settings[SettingsEnum.SUBSTRATE_XYZ_FILE.value]
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
        for requirement in schema_validation.DEPOSITION_TYPES[self.deposition_type]:
            assert (
                requirement in settings.keys()
            ), f"{requirement} required in {self.deposition_type} deposition"

        # check that the position distribution is valid
        position_distribution = distributions.get_position_distribution(
            self.position_distribution,
            self.position_distribution_parameters,
            None,
            0.0,
        )

        # check that the velocity distribution is valid
        velocity_distribution = distributions.get_velocity_distribution(
            self.velocity_distribution,
            self.velocity_distribution_parameters,
        )

        # check that the postprocessing options are valid
        if self.postprocessing is not None:
            for name, args in self.postprocessing.items():
                postprocessing.run(name, args, None, None, dry_run=True)
