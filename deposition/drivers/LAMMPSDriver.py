import os

import numpy as np
import pandas as pd
from pymatgen.io.lammps.data import LammpsData
from schema import And, Optional, Or, Schema, Use

from deposition import io, schema_validation


class LAMMPSDriver:
    """
    What happens when I put a string here
    """

    name = "LAMMPS"
    command_syntax = "${prefix} ${binary} -in ${input_file} > ${output_file}"
    schema_dictionary = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
        "timestep_scaling_from_picoseconds": And(Or(int, float), Use(schema_validation.strictly_positive)),
        "atomic_masses": list,  # list of int/floats
        "elements_in_potential": str,  # list of strings
        Optional("num_steps"): Use(schema_validation.reserved_keyword),
        str: Or(int, float, str),  # this line ensures that unlisted keys are retained after validation
    }
    schema = Schema(schema_dictionary, ignore_extra_keys=True)

    def __init__(self, driver_settings, simulation_cell):
        self.settings = self.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):
        """
        Write a set of LAMMPS input files to run the next iteration of the deposition calculation. Uses settings
        from the Deposition object.

        :param filename: name to use for input files
        :param coordinates: numpy array of coordinate data
        :param elements: list of atomic species data
        :param velocities: numpy array of velocity data
        :param iteration_stage: either "relaxation" or "deposition"
        """
        input_filename = f"{filename}.input"
        input_data_filename = f"{filename}.input_data"

        template_values = self.settings

        if iteration_stage == "relaxation":
            relaxation_num_steps = self.settings["relaxation_time_picoseconds"] * \
                                   self.settings["timestep_scaling_from_picoseconds"]
            template_values.update({"num_steps": int(relaxation_num_steps)})
        elif iteration_stage == "deposition":
            deposition_num_steps = self.settings["deposition_time_picoseconds"] * \
                                   self.settings["timestep_scaling_from_picoseconds"]
            template_values.update({"num_steps": int(deposition_num_steps)})

        # Write input file using template
        template_values.update({"filename": filename})
        template_values.update({"elements_in_potential": self.settings["elements_in_potential"]})

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
        """
        Read LAMMPS simulation data from output files

        :param filename: name to use for output files
        :return: atomic coordinates, elements, and velocities as read from the file
        """
        data = LammpsData.from_file(f"{filename}.output_data", atom_style="charge")
        coordinates = data.atoms[["x", "y", "z"]].to_numpy()
        elements = data.atoms["type"].to_list()
        velocities = data.velocities.to_numpy()
        return coordinates, elements, velocities