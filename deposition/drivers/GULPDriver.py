import os

import numpy as np
from schema import Optional, Use

from deposition import io, physics, schema_validation
from deposition.drivers.MolecularDynamicsDriver import MolecularDynamicsDriver


class GULPDriver(MolecularDynamicsDriver):
    """
    Class to interface between deposition package and GULP software

    GULPDriver defines input variables required for the driver functions to work, as well as how to call GULP on the
    command line, write GULP input files, and read GULP output files. The `schema_dictionary` defines additional
    inputs which are required when using the GULP driver.
    """
    name = "GULP"
    """String matched against input settings when initialising the driver."""

    schema_dictionary = {
        "GULP_LIB": os.path.exists,
        Optional("production_time_picoseconds"): Use(schema_validation.reserved_keyword),
        Optional("thermostat_damping"): Use(schema_validation.reserved_keyword),
        Optional("x_size"): Use(schema_validation.reserved_keyword),
        Optional("y_size"): Use(schema_validation.reserved_keyword),
        Optional("z_size"): Use(schema_validation.reserved_keyword),
        Optional("alpha"): Use(schema_validation.reserved_keyword),
        Optional("beta"): Use(schema_validation.reserved_keyword),
        Optional("gamma"): Use(schema_validation.reserved_keyword),
    }
    """
        The names and types of additional inputs for GULP:

        - GULP_LIB (path): location of GULP library folder containing provided potentials 
        - production_time_picoseconds (int or float): used in template for duration of simulation
        - x_size (float): used in template to specify simulation cell
        - y_size (float): used in template to specify simulation cell
        - z_size (float): used in template to specify simulation cell
        - alpha (float): used in template to specify simulation cell
        - beta (float): used in template to specify simulation cell
        - gamma (float): used in template to specify simulation cell
    """

    def __init__(self, driver_settings, simulation_cell):
        super().__init__(driver_settings, simulation_cell, self.schema_dictionary)
        self.set_environment_variables()

    def set_environment_variables(self):
        """
        Uses the user provided value for GULP_LIB to set the environment variable. This is essential to use the
        potentials which ship with GULP.
        """
        os.putenv("GULP_LIB", self.settings["GULP_LIB"])

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):
        """
        Write GULP input file for the next part of the deposition calculation.

        Arguments:
            filename (str): name to use for input files
            coordinates (np.array): coordinate data
            elements (list): atomic species data
            velocities (np.array): velocity data
            iteration_stage (str): either "relaxation" or "deposition"
        """
        def write_positions(filename, coordinates, elements):
            """
            Write positional data to the GULP input file

            Arguments:
                filename (str): name to use for input files
                coordinates (np.array): coordinate data
                elements (list): atomic species data
            """
            with open(filename, "a") as file:
                file.write("cartesian\n")
                for atom, xyz in zip(elements, coordinates):
                    file.write(f"{atom} {xyz[0]} {xyz[1]}, {xyz[2]}\n")

        def write_velocities(filename, velocities):
            """
            Write positional data to the GULP input file

            Arguments:
                filename (str): name to use for input files
                velocities (np.array): velocity data
            """
            with open(filename, "a") as file:
                file.write("velocities\n")
                for ii, v in enumerate(velocities):
                    file.write(f"{ii} {v[0]} {v[1]} {v[2]}\n")

        def parameters_from_simulation_cell(simulation_cell):
            """
            Get GULP friendly specification of the simulation cell from the dict

            Arguments:
                simulation_cell (dict): specification of the size and shape of the simulation cell

            Returns:
                simulation_cell (tuple):
                    - x_size
                    - y_size
                    - z_size
                    - alpha
                    - beta
                    - gamma
            """
            x_size = simulation_cell["x_max"] - simulation_cell["x_min"]
            y_size = simulation_cell["y_max"] - simulation_cell["y_min"]
            z_size = simulation_cell["z_max"] - simulation_cell["z_min"]
            alpha = simulation_cell["alpha"]
            beta = simulation_cell["beta"]
            gamma = simulation_cell["gamma"]
            return x_size, y_size, z_size, alpha, beta, gamma

        input_filename = f"{filename}.input"

        thermostat_damping = self.get_thermostat_damping(len(elements), self.settings["temperature_of_system"])
        x_size, y_size, z_size, alpha, beta, gamma = parameters_from_simulation_cell(self.simulation_cell)

        template_values = self.settings

        if iteration_stage == "relaxation":
            template_values.update({"production_time_ps": self.settings["relaxation_time_picoseconds"]})
        elif iteration_stage == "deposition":
            template_values.update({"production_time_ps": self.settings["deposition_time_picoseconds"]})

        template_values.update({"filename": filename})
        template_values.update({"thermostat_damping": thermostat_damping})
        template_values.update({"x_size": x_size})
        template_values.update({"y_size": y_size})
        template_values.update({"z_size": z_size})
        template_values.update({"alpha": alpha})
        template_values.update({"beta": beta})
        template_values.update({"gamma": gamma})

        io.write_file_using_template(input_filename, self.settings["path_to_input_template"], template_values)
        write_positions(input_filename, coordinates, elements)
        if iteration_stage == "deposition":
            write_velocities(input_filename, velocities)

    @staticmethod
    def get_thermostat_damping(num_atoms, temperature=300.0):
        """
        Calculate the required Nose-Hoover coupling constant which should give rise to canonical
        temperature fluctuations throughout the simulation. The number is derived from a fitted power
        law equation. See Section 2.4.1 in my `thesis`_.

        Arguments:
            num_atoms (int): the number of atoms in the simulation
            temperature (float): temperature of the simulation in Kelvin

        Returns:
            nose_hoover (float): the coupling constant required to give the canonical variance in the simulation

        .. _thesis: https://researchrepository.rmit.edu.au/discovery/delivery/61RMIT_INST:RMITU/12247670720001341
        """
        minimum_nose_hoover_parameter = 0.0001
        a = 610.0
        b = -49.6
        canonical_variance = physics.get_canonical_variance(num_atoms, temperature)
        nose_hoover = (np.log(canonical_variance) - np.log(a)) / b
        return max(round(nose_hoover, 6), minimum_nose_hoover_parameter)

    @staticmethod
    def read_outputs(filename):
        """
        Read simulation data from GULP output files and return coordinate, element, and velocity data.

        Arguments:
            filename (str): basename to use for reading output files

        Returns:
            coordinates, elements, velocities (tuple)
                - coordinates (np.array): coordinate data
                - elements (list): atomic species data
                - velocities (np.array): velocity data
        """
        def get_data_types(trajectory_file):
            """
            Assess the type of data contained in the trajectory file.

            Arguments:
                trajectory_file (path): GULP trajectory (.trj) file containing position, velocity, and other data

            Returns:
                list_of_data_types (list): types of data in the file, e.g. Coordinates, Velocities, Charges, etc.
            """
            list_of_data_types = list()
            with open(trajectory_file) as file:
                for line in file:
                    if line.startswith("#") and "Time" not in line:
                        data_type = line.strip("#").strip()
                        if data_type in list_of_data_types:
                            break
                        else:
                            list_of_data_types.append(data_type)
            return list_of_data_types

        def get_data_from_trajectory_file(trajectory_file, data_type, step_number=None):
            """
            Read data from the trajectory file.

            Arguments:
                trajectory_file (path): GULP trajectory (.trj) file containing position, velocity, and other data
                data_type (str): type of data to read, e.g. Coordinates, Velocities, Charges, etc.
                step_number (int or None): which step of the file to read from

            Returns:
                data (np.array): data read from the file of the given type at the given step
            """
            available_types = get_data_types(trajectory_file)
            if data_type not in available_types:
                raise ValueError(f"data type {data_type} not present")

            with open(trajectory_file) as file:
                _ = file.readline()
                num_atoms, _ = file.readline().split()

            num_header_lines = 2
            num_lines_per_step = num_header_lines + (len(available_types) * (num_atoms + 1))
            num_lines_in_file = sum(1 for _ in open(trajectory_file))
            num_steps = (num_lines_in_file - num_header_lines) / num_lines_per_step
            if step_number is None:
                step_number = num_steps
            num_lines_to_skip = num_header_lines + (num_lines_per_step * (step_number - 1))

            with open(trajectory_file) as file:
                io.throw_away_lines(file, num_lines_to_skip)
                for line in file:
                    if line.strip("#").strip() == data_type:
                        break
                data = np.empty((num_atoms, 3))
                data.fill(np.nan)
                for ii in range(num_atoms):
                    atom_data = file.readline().split()
                    for jj, value in enumerate(atom_data):
                        data[ii, jj] = value

            data = data[:, ~np.isnan(data).all(axis=0)]  # delete redundant columns of NaN values
            return data

        coordinates, elements, _ = io.read_xyz(f"{filename}.xyz")
        velocities = get_data_from_trajectory_file(f"{filename}.trg", "Velocities")
        return coordinates, elements, velocities
