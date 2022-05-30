import yaml

from deposition import distributions, input_schema, postprocessing
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
        self.strict_postprocessing = settings[SettingsEnum.STRICT_POSTPROCESSING.value]
        self.substrate_xyz_file = settings[SettingsEnum.SUBSTRATE_XYZ_FILE.value]
        self.velocity_distribution = settings[SettingsEnum.VELOCITY_DISTRIBUTION.value]
        self.velocity_distribution_parameters = settings[
            SettingsEnum.VELOCITY_DISTRIBUTION_PARAMS.value
        ]
        self.validate(settings)

    def validate(self, settings):
        """Performs additional validation not covered by the schema"""

        # check that required options for the deposition type are present
        for requirement in input_schema.DepositionTypeEnum[self.deposition_type].value:
            assert (
                requirement in settings.keys()
            ), f"{requirement} required in {self.deposition_type} deposition"

        # check that the position distribution has valid parameters
        distributions.get_position_distribution(
            self.position_distribution, None, 0.0, self.position_distribution_parameters
        )

        # check that the velocity distribution has valid parameters
        distributions.get_velocity_distribution(
            self.velocity_distribution,
            self.velocity_distribution_parameters,
        )

        # check that the postprocessing options have valid parameters
        if self.postprocessing is not None:
            for name, parameters in self.postprocessing.items():
                postprocessing.run(name, None, None, parameters, dry_run=True)

    @staticmethod
    def from_file(filename):
        """
        Read and validate a YAML file containing simulation settings.

        Arguments:
            filename (path): path to a YAML file containing settings for the simulation

        Returns:
            settings (dict): validated settings for the deposition simulation
        """
        with open(filename) as file:
            settings_dict = yaml.safe_load(file)
        settings_dict = input_schema.get_settings_schema().validate(settings_dict)
        settings = Settings(settings_dict)
        settings.validate(settings_dict)
        return settings

    def as_dict(self):
        """Returns the settings as a dictionary"""
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("__") and not callable(key)
        }
