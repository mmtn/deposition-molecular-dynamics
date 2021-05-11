import os
import shutil

import numpy as np
import pandas as pd
from pandas import DataFrame
from pymatgen.io.lammps.data import LammpsData, lattice_2_lmpbox
from pymatgen.core.lattice import Lattice

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

    def after_calculation(self, calculation_directory, archived_directory):
        shutil.move("log.cite", archived_directory)
        shutil.move("log.lammps", archived_directory)

    def write_inputs(self, filename, coordinates, elements, velocities=None):
        # Write input file using template system
        settings = self.settings
        settings["filename"] = filename
        species = settings["atomic_species"]
        settings["species_list"] = " ".join(species)
        if velocities is None:
            settings["num_steps"] = settings["relaxation_num_steps"]
        else:
            settings["num_steps"] = settings["deposition_num_steps"]
        io.write_file_using_template(f"{filename}.input", self.input_template, settings)

        # Convert from string labels to number labels where required
        elements = [(species.index(ii) + 1) if ii in species else ii for ii in elements]
        element_integers = [int(ii) for ii in elements]
        num_atoms = len(elements)
        indices = range(1, num_atoms + 1)
        masses = settings["atomic_masses"]
        mass_indices = range(1, len(masses) + 1)

        # Create LammpsData object from system information
        lammps_box, _ = lattice_2_lmpbox(Lattice.from_parameters(**self.substrate))
        masses_df = DataFrame(masses, index=mass_indices, columns=["mass"])
        charges_df = DataFrame(np.zeros((num_atoms, 1)), index=indices, columns=["q"])
        elements_df = DataFrame(element_integers, index=indices, columns=["type"])
        coordinates_df = DataFrame(coordinates, index=indices, columns=["x", "y", "z"])
        atoms_df = pd.concat((elements_df, charges_df, coordinates_df), axis=1)
        data = LammpsData(lammps_box, masses_df, atoms_df, atom_style="charge")
        if velocities is not None:
            data.velocities = DataFrame(velocities, index=indices, columns=["vx", "vy", "vz"])
        data.write_file(f"{filename}.input_data")

    @staticmethod
    def read_outputs(filename):
        data = LammpsData.from_file(f"{filename}.output_data", atom_style="charge")
        coordinates = data.atoms[["x", "y", "z"]].to_numpy()
        elements = data.atoms["type"].to_list()
        velocities = data.velocities.to_numpy()
        return coordinates, elements, velocities
