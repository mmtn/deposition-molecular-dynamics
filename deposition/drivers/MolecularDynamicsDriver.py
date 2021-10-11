import os

from schema import And, Or, Optional, Schema, Use

from deposition import schema_validation


class MolecularDynamicsDriver:
    """
    Generic molecular dynamics driver class
    """

    generic_schema_dict = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
    }

    command = "${prefix} ${binary} < ${input_file} > ${output_file}"

    def __init__(self, driver_settings, simulation_cell, driver_schema_dict=None, driver_reserved_keywords=None,
                 driver_command=None):

        # add driver specific variables to schema
        if driver_schema_dict is not None:
            self.generic_schema_dict.update(driver_schema_dict)

        # add reserved keywords to schema
        if driver_reserved_keywords is not None:
            reserved_keywords_schema_dict = {
                Optional(keyword): Use(schema_validation.reserved_keyword)
                for keyword in driver_reserved_keywords
            }
            self.generic_schema_dict.update(reserved_keywords_schema_dict)
        else:
            reserved_keywords_schema_dict = {}

        if driver_command is not None:
            self.command = driver_command

        # this ensures that keys which are not explicitly listed are retained after validation
        self.generic_schema_dict.update({str: Or(int, float, str)})

        self.schema = Schema(self.generic_schema_dict, ignore_extra_keys=True)
        self.settings = self.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]
