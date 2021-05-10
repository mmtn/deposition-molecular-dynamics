import os
import shutil

from src import io


class LAMMPSDriver:
    def __init__(self, driver_settings, substrate):
        self.settings = driver_settings
        self.substrate = substrate
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.name = "LAMMPS"
        self.binary = "~/work/repos/lammps/src/lmp_serial"
        self.command_syntax = "${prefix} ${binary} < ${input_file} > ${output_file}"
        self.input_template = f"{self.path}/lammps_input_template.txt"
        self.system_template = f"{self.path}/lammps_system_template.txt"

    def after_calculation(self, calculation_directory, archived_directory):
        shutil.move("log.cite", archived_directory)
        shutil.move("log.lammps", archived_directory)

    def write_inputs(self, filename, coordinates, elements, velocities):
        def write_masses(filename, atomic_weights):
            with open(filename, "a") as file:
                file.write("Masses\n\n")
                for ii, weight in enumerate(atomic_weights):
                    file.write(f"{ii + 1} {weight}\n")
                file.write("\n")

        def write_positions(filename, coordinates, elements):
            with open(filename, "a") as file:
                file.write("Atoms\n\n")
                for atom_number, (atom, xyz) in enumerate(zip(elements, coordinates)):
                    file.write(f"{atom_number + 1} {atom} 0.0 {xyz[0]} {xyz[1]} {xyz[2]}\n")
                file.write("\n")

        def write_velocities(filename, velocities):
            with open(filename, "a") as file:
                file.write("Velocities\n\n")
                for atom_number, v in enumerate(velocities):
                    file.write(f"{atom_number + 1} {v[0]} {v[1]} {v[2]}\n")
                file.write("\n")

        input_filename = f"{filename}.input"
        system_filename = f"{filename}.system"
        template = self.settings
        template.update(self.substrate)
        template["filename"] = filename
        template["num_atoms"] = len(elements)
        template["num_atom_types"] = len(template["atomic_weights"])
        template["num_steps"] = template["relaxation_num_steps"] if velocities is None \
            else template["deposition_num_steps"]

        io.write_file_using_template(self.input_template, input_filename, template)
        io.write_file_using_template(self.system_template, system_filename, template)

        write_masses(system_filename, template["atomic_weights"])
        write_positions(system_filename, coordinates, elements)
        if velocities is not None:
            write_velocities(system_filename, velocities)

    def read_outputs(self, filename):
        def read_lammps_data(filename):
            with open(filename, "r") as file:
                comment = file.readline()
                blank = file.readline()
                num_atoms = file.readline().split()[0]
                num_atom_types = file.readline().split()[0]
                

        def read_lammps_velocities(filename):
            num_lines = sum(1 for _ in open(filename))
            with open(filename, "r") as file:
                io.throw_away_lines(file, num_lines - num_atoms)
                data = [line.split() for line in file]
                return [
                    [float(atom[1]), float(atom[2]), float(atom[3])]
                    for atom in data
                ]

        coordinates, elements, num_atoms = io.read_xyz(f"{filename}.xyz")
        velocities = read_lammps_velocities(f"{filename}.velocities")
        return coordinates, elements, velocities
