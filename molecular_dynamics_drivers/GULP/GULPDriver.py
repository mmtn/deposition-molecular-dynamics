import itertools
import os

import numpy as np
from schema import Schema, And, Or, Use, Optional, SchemaError

from src import io, physics, schema_validation


class GULPDriver:
    name = "GULP"
    command_syntax = "${prefix} ${binary} < ${input_file} > ${output_file}"
    schema = Schema({
        "name": str,
        "path_to_binary": os.path.exists,
        "path_to_input_template": os.path.exists,
        "elements_in_potential": str,  # list of strings
        "atomic_masses": list,  # list of int/floats
        "deposition_num_steps": And(int, Use(schema_validation.strictly_positive)),
        "relaxation_num_steps": And(int, Use(schema_validation.strictly_positive)),
        "velocity_scaling_from_metres_per_second": And(Or(int, float), Use(schema_validation.strictly_positive)),
        object: object},  # this line ensures that unlisted keys are also kept after validation
        ignore_extra_keys=True
    )

    GULP_LIBRARY_PATH = "path/to/gulp/libraries"  # TODO: check env variable name and path

    def __init__(self, driver_settings, simulation_cell):
        self.settings = GULPDriver.schema.validate(driver_settings)
        self.simulation_cell = simulation_cell
        self.binary = self.settings["path_to_binary"]
        self.set_environment_variables()

    @staticmethod
    def set_environment_variables():
        os.putenv("GULP_LIBRARY", GULPDriver.GULP_LIBRARY_PATH)

    def write_inputs(self, filename, coordinates, elements, velocities):
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

        def thermostat_damping(num_atoms, temperature=300.0):
            """
            Calculate the required Nose-Hoover coupling constant which should give rise to canonical
            temperature fluctuations throughout the simulation. The number is derived from a fitted power
            law equation.

            :param num_atoms: the number of atoms in the simulation
            :param temperature: temperature of the simulation in Kelvin
            :return nose_hoover: the coupling constant required to give the canonical
                                 variance in the simulation
            """
            minimum_nose_hoover_parameter = 0.0001
            a = 610.0
            b = -49.6
            canonical_variance = physics.get_canonical_variance(num_atoms, temperature)
            nose_hoover = (np.log(canonical_variance) - np.log(a)) / b
            return max(round(nose_hoover, 6), minimum_nose_hoover_parameter)

        input_filename = f"{filename}.input"
        settings = self.settings
        settings.update(self.simulation_cell)
        settings["thermostat_damping"] = thermostat_damping(len(elements), settings["temperature_of_system"])
        settings["filename"] = filename
        if velocities is None:
            settings["production_time_ps"] = settings["relaxation_time_ps"]
        else:
            settings["production_time_ps"] = settings["deposition_time_ps"]
        io.write_file_using_template(input_filename, self.input_template, settings)
        write_positions(input_filename, coordinates, elements)
        if velocities is not None:
            write_velocities(input_filename, velocities)

    def read_outputs(self, filename):
        def get_trajectory_info(trajectory_file):
            """ Get the number of lines in the file and the number of atoms """
            def get_num_datasets(trg_file):
                num_data_sets = 0
                with open(trg_file) as file:
                    for ii, line in enumerate(file):
                        if ii > 4:
                            if '#' == line[0]:
                                num_data_sets += 1
                            if 'Time' in line:
                                break
                return num_data_sets

            def get_num_atoms(trg_file):
                with open(trg_file) as file:
                    file.readline()
                    split_line = file.readline().split()
                    return int(split_line[0])

            num_atoms = get_num_atoms(trajectory_file)
            num_lines = sum(1 for _ in open(trajectory_file))
            header_lines = 2
            step_header_lines = 2
            num_data_sets = get_num_datasets(trajectory_file)
            lines_per_data_set = num_atoms + 1
            lines_per_step = step_header_lines + (num_data_sets * lines_per_data_set)
            total_num_steps = (num_lines - header_lines) / lines_per_step
            return num_lines, num_atoms, lines_per_step, int(total_num_steps), header_lines

        def get_line_numbers_for_data(trajectory_file, data_type, step_num=None):
            num_lines, num_atoms, lines_per_step, total_num_steps, header_lines = get_trajectory_info(trajectory_file)
            lines_per_data_set = num_atoms + 1
            step_header_lines = 2

            if step_num is None:
                step_num = total_num_steps
            if step_num > total_num_steps or step_num < 1:
                raise ValueError('Step number must be positive and less than total number of steps')

            effective_step_num = step_num - 1
            data_start = header_lines + (lines_per_step * effective_step_num) + 1

            if data_type == 'positions':
                data_start += step_header_lines
            elif data_type == 'velocities':
                data_start += step_header_lines + lines_per_data_set
            elif data_type == "derivatives":
                data_start += step_header_lines + (2 * lines_per_data_set)
            elif data_type == "site_energies":
                data_start += step_header_lines + (3 * lines_per_data_set)
            elif data_type == "charges":
                data_start += step_header_lines + (4 * lines_per_data_set)
            else:
                raise ValueError(
                    "Data types available: positions, velocities, derivatives, site_energies, charges"
                )

            data_end = data_start + num_atoms
            return data_start, data_end

        def get_data_from_trajectory_file(trajectory_file, data_type, step_num=None):
            data_start, data_end = get_line_numbers_for_data(trajectory_file, data_type, step_num)
            with open(trajectory_file) as file:
                split_lines = [
                    line.split()
                    for line in itertools.islice(file, int(data_start), int(data_end))
                ]

            return [
                np.array([float(ii[0]), float(ii[1]), float(ii[2])])
                for ii in split_lines
            ]

        coordinates, elements, num_atoms = io.read_xyz(f"{filename}.xyz")
        velocities = get_data_from_trajectory_file(f"{filename}.trj", "velocities")
        return coordinates, elements, velocities
