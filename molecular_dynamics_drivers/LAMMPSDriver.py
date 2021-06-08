import os
import re

import numpy as np
import pandas as pd
from pymatgen.io.lammps.data import LammpsData
from schema import Schema, And, Or, Use, Optional, SchemaError

from src import io, schema_validation


class LAMMPSDriver:
    name = "LAMMPS"
    command_syntax = "${prefix} ${binary} -in ${input_file} > ${output_file}"

    schema_dictionary = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "elements_in_potential": str,  # list of strings
        "atomic_masses": list,  # list of int/floats
        "deposition_num_steps": And(int, Use(schema_validation.strictly_positive)),
        "relaxation_num_steps": And(int, Use(schema_validation.strictly_positive)),
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
        object: object,  # this line ensures that unlisted keys are also kept after validation
    }

    reserved_keywords = [
        "filename",
        "num_steps",
    ]

    for key in reserved_keywords:
        schema_dictionary.update({Optional(key): Use(schema_validation.reserved_keyword)})

    schema = Schema(schema_dictionary, ignore_extra_keys=True)

    def __init__(self, driver_settings, simulation_cell):
        self.settings = self.validate_schema_and_input_template(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]

    @staticmethod
    def validate_schema_and_input_template(driver_settings):
        settings = LAMMPSDriver.schema.validate(driver_settings)

        # regex matches any variable placeholder starting with the $ character, either ${with} or $without braces
        template_variable_regular_expression = r"[\$][{]?([a-z,A-Z][_,a-z,A-Z,0-9]*)[}]?"

        with open(settings["path_to_input_template"]) as file:
            template_variables = re.findall(template_variable_regular_expression, file.read())

        additional_keys = [key for key in template_variables if key not in LAMMPSDriver.schema.schema.keys()]

        for key in additional_keys:
            if key in LAMMPSDriver.reserved_keywords:  # ignore reserved keywords
                continue
            elif key in settings:  # a value has been provided
                continue
            else:  # unknown key
                raise SchemaError(f"variable '${key}' present in input template but has no set value")

        return settings

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):

        template_values = self.settings
        input_filename = f"{filename}.input"
        input_data_filename = f"{filename}.input_data"

        # Write input file using template
        template_values.update({"filename": filename})
        template_values.update({"elements_in_potential": self.settings["elements_in_potential"]})
        if iteration_stage == "relaxation":
            template_values.update({"num_steps": self.settings["relaxation_num_steps"]})
        elif iteration_stage == "deposition":
            template_values.update({"num_steps": self.settings["deposition_num_steps"]})

        io.write_file_using_template(input_filename, self.settings["path_to_input_template"], template_values)

        # Convert from string labels to number labels where required, + 1 because of zero-indexing
        list_of_elements_in_potential = self.settings["elements_in_potential"].split()
        for element_index, element in enumerate(elements):
            if element in list_of_elements_in_potential:
                elements[element_index] = list_of_elements_in_potential.index(element) + 1
        element_integers = [int(element) for element in elements]

        # Set up indices for pandas dataframes
        atom_indices = range(1, len(elements) + 1)
        mass_indices = range(1, len(self.settings["atomic_masses"]) + 1)

        # Create LammpsData object from system information
        masses_dataframe = pd.DataFrame(self.settings["atomic_masses"],
                                        index=mass_indices,
                                        columns=["mass"])
        charges_dataframe = pd.DataFrame(np.zeros(((len(elements)), 1)),
                                         index=atom_indices,
                                         columns=["q"])
        elements_dataframe = pd.DataFrame(element_integers,
                                          index=atom_indices,
                                          columns=["type"])
        coordinates_dataframe = pd.DataFrame(coordinates,
                                             index=atom_indices,
                                             columns=["x", "y", "z"])
        combined_atomic_dataframe = pd.concat((elements_dataframe, charges_dataframe, coordinates_dataframe), axis=1)
        lammps_data_object = LammpsData(self.simulation_cell["lammps_box"],
                                        masses_dataframe,
                                        combined_atomic_dataframe,
                                        atom_style="charge")

        # Maintain atomic velocities between relaxation and deposition stages of each iteration
        if iteration_stage == "deposition":
            lammps_data_object.velocities = pd.DataFrame(velocities,
                                                         index=atom_indices,
                                                         columns=["vx", "vy", "vz"])

        lammps_data_object.write_file(input_data_filename)

    @staticmethod
    def read_outputs(filename):
        data = LammpsData.from_file(f"{filename}.output_data", atom_style="charge")
        coordinates = data.atoms[["x", "y", "z"]].to_numpy()
        elements = data.atoms["type"].to_list()
        velocities = data.velocities.to_numpy()
        return coordinates, elements, velocities