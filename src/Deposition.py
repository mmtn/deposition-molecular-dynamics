import logging
from datetime import datetime as dt

import numpy as np
import yaml
from pymatgen.io.lammps.data import lattice_2_lmpbox
from pymatgen.core.lattice import Lattice

from src import io, Iteration


class Deposition:
    def __init__(self, settings_filename):
        self.settings = io.read_yaml(settings_filename)
        self.driver_settings = io.read_yaml(self.settings["driver_settings"])
        self.substrate = self.get_substrate()
        self.driver = self.get_driver()
        self.max_iterations = self.settings["maximum_total_iterations"]
        self.max_failures = self.settings["maximum_sequential_failures"]
        self.iteration_number, self.num_sequential_failures, self.pickle_location = self.read_status()

    def get_substrate(self):
        substrate = io.read_yaml(self.settings["substrate_information"])
        lammps_box, _ = lattice_2_lmpbox(Lattice.from_parameters(**substrate))
        ((xlo, xhi), (ylo, yhi), (zlo, zhi)) = [[entry for entry in axis] for axis in lammps_box.bounds]
        xy, xz, yz = (0, 0, 0) if lammps_box.tilt is None else lammps_box.tilt
        substrate["xlo"] = xlo
        substrate["xhi"] = xhi
        substrate["ylo"] = ylo
        substrate["yhi"] = yhi
        substrate["zlo"] = zlo
        substrate["zhi"] = zhi
        substrate["xy"] = xy
        substrate["xz"] = xz
        substrate["yz"] = yz
        substrate["x_vector"] = np.array((xhi - xlo, 0, 0))
        substrate["y_vector"] = np.array((xy, yhi - ylo, 0))
        substrate["z_vector"] = np.array((xz, yz, zhi - zlo))
        substrate["lammps_box"] = lammps_box
        return substrate

    def get_driver(self):
        driver_name = self.driver_settings["name"]
        if driver_name.upper() == "GULP":
            from md_drivers.GULP import GULPDriver
            return GULPDriver.GULPDriver(self.driver_settings, self.substrate)
        elif driver_name.upper() == "LAMMPS":
            from md_drivers.LAMMPS import LAMMPSDriver
            return LAMMPSDriver.LAMMPSDriver(self.driver_settings, self.substrate)
        else:
            raise NotImplementedError(f"specified MD driver \'{driver_name}\' not found")

    def read_status(self):
        """Reads information about the current state of the deposition simulation"""
        try:
            status = io.read_yaml("status.yaml")
            iteration_number = int(status["iteration_number"])
            num_sequential_failures = int(status["num_sequential_failures"])
            pickle_location = status["pickle_location"]
            return iteration_number, num_sequential_failures, pickle_location
        except FileNotFoundError:
            logging.info("no status.yaml file found")
            return (None, None, None)

    def write_status(self):
        """Writes information about the current state of the deposition simulation"""
        status = {
            "last_updated": dt.now(),
            "iteration_number": self.iteration_number,
            "num_sequential_failures": self.num_sequential_failures,
            "pickle_location": self.pickle_location
        }
        with open("status.yaml", "w") as file:
            yaml.dump(status, file)

    def first_run(self):
        self.iteration_number = 1
        self.num_sequential_failures = 0
        self.pickle_location = "initial_positions.pickle"
        coordinates, elements, _ = io.read_xyz(self.settings["substrate_xyz_file"])
        io.write_state(coordinates, elements, velocities=None, pickle_location=self.pickle_location)
        io.make_directories(("current", "iterations", "failed"))
        self.write_status()

    def run_loop(self):
        if self.iteration_number is None:
            self.first_run()
        while (self.iteration_number <= self.max_iterations) and (self.num_sequential_failures <= self.max_failures):
            iteration = Iteration.Iteration(self.driver, self.settings, self.iteration_number, self.pickle_location)
            success, self.pickle_location = iteration.run()
            self.num_sequential_failures = 0 if success else self.num_sequential_failures + 1
            self.iteration_number += 1
            self.write_status()
        return 0
