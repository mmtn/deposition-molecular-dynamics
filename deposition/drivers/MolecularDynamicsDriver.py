import os

from schema import And, Or, Schema, Use

from deposition import schema_validation


class MolecularDynamicsDriver:
    """
    Generic molecular dynamics driver class
    """

    generic_schema_dictionary = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
    }

    command = "${prefix} ${binary} < ${input_file} > ${output_file}"

    def __init__(self, driver_settings, simulation_cell, driver_schema_dictionary=None, driver_command=None):
        if driver_schema_dictionary is not None:
            self.generic_schema_dictionary.update(driver_schema_dictionary)

        if driver_command is not None:
            self.command = driver_command

        self.generic_schema_dictionary.update({str: Or(int, float, str)})
        # this ensures that keys which are not explicitly listed are retained after validation

        self.schema = Schema(self.generic_schema_dictionary, ignore_extra_keys=True)
        self.settings = self.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]
