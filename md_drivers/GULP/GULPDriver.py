import itertools
import os
import numpy as np

from src import io, physics


class GULPDriver:
    def __init__(self, driver_settings, substrate):
        self.settings = driver_settings
        self.substrate = substrate
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.name = "GULP"
        self.binary = "gulp"
        self.command_syntax = "${prefix} ${binary} < ${input_file} > ${output_file}"
        self.input_template = f"{self.path}/gulp_input_template.txt"
        self.set_environment_variables()

    def set_environment_variables(self):
        os.putenv("GULP_LIBRARY", "path/to/gulp/libraries")  # TODO: check env variable name and path

    def after_calculation(self):
        pass

    def write_inputs(self, filename, coordinates, elements, velocities):
        def write_positions(filename, coordinates, elements):
            with open(filename, "a") as file:
                file.write("cartesian\n")
                for atom, xyz in zip(elements, coordinates):
                    file.write(f"{atom} {xyz[0]} {xyz[1]}, {xyz[2]}\n")

        def write_velocities(filename, velocities):
            with open(filename, "a") as file:
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
        template = self.settings
        template.update(self.substrate)
        template["thermostat_damping"] = thermostat_damping(len(elements), template["temperature_of_system"])
        template["filename"] = filename
        if velocities is None:
            template["production_time_ps"] = template["relaxation_time_ps"]
        else:
            template["production_time_ps"] = template["deposition_time_ps"]

        io.write_file_using_template(self.input_template, input_filename, template)

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
