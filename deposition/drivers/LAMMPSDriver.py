import numpy as np
import pandas as pd
from pymatgen.io.lammps.data import LammpsData
from schema import And, Optional, Or, Use

from deposition import io, schema_validation
from deposition.drivers.MolecularDynamicsDriver import MolecularDynamicsDriver


class LAMMPSDriver(MolecularDynamicsDriver):
    """
    Class to interface between deposition package and LAMMPS software

    LAMMPSDriver defines input variables required for the driver functions to work, as well as how to call LAMMPS on the
    command line, write LAMMPS input files, and read LAMMPS output files. The `schema_dict` defines additional
    inputs which are required when using the LAMMPS driver.
    """

    name = "LAMMPS"
    """String matched against input settings when initialising the driver."""

    schema_dict = {
        "atomic_masses": list,  # list of int/floats
        "elements_in_potential": str,  # list of strings
        "timestep_scaling_from_picoseconds": And(Or(int, float), Use(schema_validation.strictly_positive)),
        Optional("num_steps"): Use(schema_validation.reserved_keyword),
    }
    """
    The names and types of additional inputs for LAMMPS:
    
    - atomic_masses (list): masses of elements in the potential in atomic mass units
    - elements_in_potential (str): space separated list of elements in the potential, e.g. "Al O H"
    - timestep_scaling_from_picoseconds (int/float): required to calculate `num_steps` from the simulation times
    
    Note: the length and order of `atomic_masses` and `elements_in_potential` must match.
    """

    reserved_keywords = [
        "num_steps",
    ]
    """
    The names of keywords used internally for running LAMMPS simulations:
    
    - num_steps (int): the total number of steps in the calculation (total time / timestep)
    """

    command = "${prefix} ${binary} -in ${input_file} > ${output_file}"
    """Template used when calling LAMMPS subprocesses."""

    def __init__(self, driver_settings, simulation_cell):
        super().__init__(
            driver_settings,
            simulation_cell,
            driver_schema_dict=self.schema_dict,
            driver_reserved_keywords=self.reserved_keywords,
            driver_command=self.command
        )

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):
        """
        Write LAMMPS input file and input system data to run the next part of the deposition calculation.

        Arguments:
            filename (str): name to use for input files
            coordinates (np.array): coordinate data
            elements (list): atomic species data
            velocities (np.array): velocity data
            iteration_stage (str): either "relaxation" or "deposition"
        """
        input_filename = f"{filename}.input"
        input_data_filename = f"{filename}.input_data"

        template_values = self.settings.copy()
        scaling = self.settings["timestep_scaling_from_picoseconds"]

        if iteration_stage == "relaxation":
            relaxation_num_steps = self.settings["relaxation_time_picoseconds"] * scaling
            template_values.update({"num_steps": int(relaxation_num_steps)})
        elif iteration_stage == "deposition":
            deposition_num_steps = self.settings["deposition_time_picoseconds"] * scaling
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
        masses_dataframe = pd.DataFrame(self.settings["atomic_masses"], index=mass_indices, columns=["mass"])
        charges_dataframe = pd.DataFrame(np.zeros(((len(elements)), 1)), index=atom_indices, columns=["q"])
        elements_dataframe = pd.DataFrame(element_integers, index=atom_indices, columns=["type"])
        coordinates_dataframe = pd.DataFrame(coordinates, index=atom_indices, columns=["x", "y", "z"])
        combined_atomic_dataframe = pd.concat((elements_dataframe, charges_dataframe, coordinates_dataframe), axis=1)

        lammps_data_object = LammpsData(
            self.simulation_cell["lammps_box"],
            masses_dataframe,
            combined_atomic_dataframe,
            atom_style="charge"
        )

        # Maintain atomic velocities between relaxation and deposition stages of each iteration
        if iteration_stage == "deposition":
            lammps_data_object.velocities = pd.DataFrame(velocities, index=atom_indices, columns=["vx", "vy", "vz"])

        lammps_data_object.write_file(input_data_filename)

    @staticmethod
    def read_outputs(filename):
        """
        Read simulation data from LAMMPS output files and return coordinate, element, and velocity data.

        Arguments:
            filename (str): basename to use for reading output files

        Returns:
            coordinates, elements, velocities (tuple)
                - coordinates (np.array): coordinate data
                - elements (list): atomic species data
                - velocities (np.array): velocity data
        """
        data = LammpsData.from_file(f"{filename}.output_data", atom_style="charge")
        coordinates = data.atoms[["x", "y", "z"]].to_numpy()
        elements = data.atoms["type"].to_list()
        velocities = data.velocities.to_numpy()
        return coordinates, elements, velocities
