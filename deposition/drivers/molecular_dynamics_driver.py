import os

from schema import And, Optional, Or, Schema, Use

from deposition.input_schema import reserved_keyword, strictly_positive


class MolecularDynamicsDriver:
    """
    Generic molecular dynamics driver class
    """

    _command = "${prefix} ${binary} ${arguments} < ${input_file} > ${output_file}"

    _schema_dict = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "velocity_scaling_from_metres_per_second": And(
            Or(int, float), Use(strictly_positive)
        ),
        Optional("command_line_args", default=""): str,
    }

    _reserved_keywords = [
        "filename",
    ]

    def __init__(
        self,
        driver_settings,
        simulation_cell,
        command=None,
        schema_dict=None,
        reserved_keywords=None,
    ):

        if command is not None:
            self.command = command
        else:
            self.command = self._command

        if schema_dict is not None:
            self._schema_dict.update(schema_dict)

        if reserved_keywords is not None:
            [self._reserved_keywords.append(kw) for kw in reserved_keywords]

        # add reserved keywords
        reserved_keywords_schema_dict = {
            Optional(kw): Use(reserved_keyword) for kw in self._reserved_keywords
        }
        self._schema_dict.update(reserved_keywords_schema_dict)
        self._schema_dict.update(
            {str: Or(int, float, str)}
        )  # retain keys which are not explicitly listed

        self.schema = Schema(self._schema_dict, ignore_extra_keys=True)
        self.settings = self.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]

    def get_reserved_keywords(self):
        """Returns a list of global and driver specific reserved keywords"""
        return self._reserved_keywords
