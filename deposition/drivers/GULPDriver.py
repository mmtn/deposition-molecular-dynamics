import os
import numpy as np
from schema import Schema, And, Or, Use, Optional
from deposition import io, physics, schema_validation


class GULPDriver:
    name = "GULP"
    command_syntax = "${prefix} ${binary} < ${input_file} > ${output_file}"
    schema_dictionary = {
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
        "GULP_LIB": os.path.exists,
        Optional("production_time_picoseconds"): Use(schema_validation.reserved_keyword),
        Optional("thermostat_damping"): Use(schema_validation.reserved_keyword),
        Optional("x_size"): Use(schema_validation.reserved_keyword),
        Optional("y_size"): Use(schema_validation.reserved_keyword),
        Optional("z_size"): Use(schema_validation.reserved_keyword),
        Optional("alpha"): Use(schema_validation.reserved_keyword),
        Optional("beta"): Use(schema_validation.reserved_keyword),
        Optional("gamma"): Use(schema_validation.reserved_keyword),
        str: Or(int, float, str),  # this line ensures that unlisted keys are retained after validation
    }
    schema = Schema(schema_dictionary, ignore_extra_keys=True)

    def __init__(self, driver_settings, simulation_cell):
        self.settings = GULPDriver.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]
        self.set_environment_variables()

    def set_environment_variables(self):
        os.putenv("GULP_LIB", self.settings["GULP_LIB"])

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):
        def write_positions(filename, coordinates, elements):
            with open(filename, "a") as file:
                file.write("cartesian\n")
                for atom, xyz in zip(elements, coordinates):
                    file.write(f"{atom} {xyz[0]} {xyz[1]}, {xyz[2]}\n")

        def write_velocities(filename, velocities):
            with open(filename, "a") as file:
                file.write("velocities\n")
                for ii, v in enumerate(velocities):
                    file.write(f"{ii} {v[0]} {v[1]} {v[2]}\n")

        def get_thermostat_damping(num_atoms, temperature=300.0):
            """
            Calculate the required Nose-Hoover coupling constant which should give rise to canonical
            temperature fluctuations throughout the simulation. The number is derived from a fitted power
            law equation.

            :param num_atoms: the number of atoms in the simulation
            :param temperature: temperature of the simulation in Kelvin
            :return nose_hoover: the coupling constant required to give the canonical variance in the simulation
            """
            minimum_nose_hoover_parameter = 0.0001
            a = 610.0
            b = -49.6
            canonical_variance = physics.get_canonical_variance(num_atoms, temperature)
            nose_hoover = (np.log(canonical_variance) - np.log(a)) / b
            return max(round(nose_hoover, 6), minimum_nose_hoover_parameter)

        def parameters_from_simulation_cell(simulation_cell):
            x_size = simulation_cell["x_max"] - simulation_cell["x_min"]
            y_size = simulation_cell["y_max"] - simulation_cell["y_min"]
            z_size = simulation_cell["z_max"] - simulation_cell["z_min"]
            alpha = simulation_cell["alpha"]
            beta = simulation_cell["beta"]
            gamma = simulation_cell["gamma"]
            return x_size, y_size, z_size, alpha, beta, gamma

        input_filename = f"{filename}.input"

        thermostat_damping = get_thermostat_damping(len(elements), self.settings["temperature_of_system"])
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
    def read_outputs(filename):
        def get_data_types(trajectory_file):
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
