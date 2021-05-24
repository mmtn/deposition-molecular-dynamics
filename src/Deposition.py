import numpy as np
from pymatgen.io.lammps.data import lattice_2_lmpbox
from pymatgen.core.lattice import Lattice

from src import io, Iteration


class Deposition:
    def __init__(self, settings_filename):
        self.settings = io.read_yaml(settings_filename)
        self.substrate = self.get_substrate()
        self.driver_settings = io.read_yaml(self.settings["driver_settings"])
        self.driver = self.get_driver()
        self.iteration_number, self.num_sequential_failures, _ = io.read_status()
        self.command_prefix = self.settings["command_prefix"]
        self.max_iterations = self.settings["maximum_total_iterations"]
        self.max_failures = self.settings["maximum_sequential_failures"]

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
        substrate["xvec"] = np.array((xhi - xlo, 0, 0))
        substrate["yvec"] = np.array((xy, yhi - ylo, 0))
        substrate["zvec"] = np.array((xz, yz, zhi - zlo))
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

    def first_run(self):
        coordinates, elements, _ = io.read_xyz(self.settings["substrate_xyz_file"])
        io.make_directories(("current", "iterations", "failed"))
        pickle_location = "initial_positions.pickle"
        io.write_state(coordinates, elements, velocities=None, pickle_file=pickle_location)
        io.write_status(self.iteration_number, self.num_sequential_failures, pickle_location=pickle_location)

    def run_loop(self):
        if self.iteration_number == 1:
            self.first_run()
        while (self.iteration_number <= self.max_iterations) and (self.num_sequential_failures <= self.max_failures):
            iteration = Iteration.Iteration(self.driver, self.settings, self.command_prefix)
            success, pickle_location = iteration.run()
            if success:
                self.num_sequential_failures = 0
            else:
                self.num_sequential_failures += 1
            self.iteration_number += 1
            io.write_status(self.iteration_number, self.num_sequential_failures, pickle_location)
        return 0
