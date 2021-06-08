import logging
from datetime import datetime as dt

import numpy as np
from pymatgen.io.lammps.data import lattice_2_lmpbox
from pymatgen.core.lattice import Lattice

from src import schema_validation, io, Iteration


class Deposition:
    status_filename = "status.yaml"
    working_directory = "current"
    success_directory = "iterations"
    failure_directory = "failed"

    def __init__(self, settings_filename):
        """
        :param settings_filename: path to YAML file
        :type settings_filename: str
        """
        self.settings = self.get_settings(settings_filename)
        self.simulation_cell = self.get_simulation_cell()
        self.driver = self.get_molecular_dynamics_driver()
        self.iteration_number, self.num_sequential_failures, self.pickle_location = self.read_status()

    @staticmethod
    def get_settings(settings_filename):
        """
        Read and validate the YAML file containing simulation settings

        :param settings_filename: path to YAML file
        :type settings_filename: str
        :return settings: validated dictionary of settings
        :rtype settings: dict
        """
        settings = io.read_yaml(settings_filename)
        settings = schema_validation.settings_schema.validate(settings)
        return settings

    def get_simulation_cell(self):
        """
        Read information about the simulation cell from the specified YAML file.
        Additional geometry is then calculated using routines from the `pymatgen` module.

        :return simulation_cell: data from YAML file and additional geometry data
        :rtype simulation_cell: dict
        """
        simulation_cell = io.read_yaml(self.settings["simulation_cell_data"])
        simulation_cell = schema_validation.simulation_cell_schema.validate(simulation_cell)
        lammps_box, _ = lattice_2_lmpbox(Lattice.from_parameters(**simulation_cell))

        if lammps_box.tilt is None:
            tilt_xy, tilt_xz, tilt_yz = (0, 0, 0)
        else:
            tilt_xy, tilt_xz, tilt_yz = lammps_box.tilt

        x_min = lammps_box.bounds[0][0]
        x_max = lammps_box.bounds[0][1]
        y_min = lammps_box.bounds[1][0]
        y_max = lammps_box.bounds[1][1]
        z_min = lammps_box.bounds[2][0]
        z_max = lammps_box.bounds[2][1]

        additional_geometry_information = {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "z_min": z_min,
            "z_max": z_max,
            "tilt_xy": tilt_xy,
            "tilt_xz": tilt_xz,
            "tilt_yz": tilt_yz,
            "x_vector": np.array((x_max - x_min, 0, 0)),
            "y_vector": np.array((tilt_xy, y_max - y_min, 0)),
            "z_vector": np.array((tilt_xz, tilt_yz, z_max - z_min)),
            "lammps_box": lammps_box
        }

        simulation_cell.update(additional_geometry_information)

        return simulation_cell

    def get_molecular_dynamics_driver(self):
        """
        Initialise an instance of the driver for the specified molecular dynamics software

        The instance must provide the following methods:
        - write_inputs(filename, coordinates, elements, velocities, iteration_stage)
        - read_outputs(filename)

        :return driver:
        """
        driver_settings = io.read_yaml(self.settings["driver_settings"])
        if driver_settings["name"].upper() == "GULP":
            from molecular_dynamics_drivers.GULP import GULPDriver
            driver = GULPDriver.GULPDriver(driver_settings, self.simulation_cell)
        elif driver_settings["name"].upper() == "LAMMPS":
            from molecular_dynamics_drivers import LAMMPSDriver
            driver = LAMMPSDriver.LAMMPSDriver(driver_settings, self.simulation_cell)
        else:
            raise NotImplementedError(f"specified MD driver \'{driver_settings['name']}\' not found")
        return driver

    @staticmethod
    def read_status():
        """Reads information about the current state of the deposition simulation"""
        try:
            status = io.read_yaml(Deposition.status_filename)
            iteration_number = int(status["iteration_number"])
            num_sequential_failures = int(status["num_sequential_failures"])
            pickle_location = status["pickle_location"]
            return iteration_number, num_sequential_failures, pickle_location
        except FileNotFoundError:
            logging.info("no status.yaml file found")
            return None, None, None

    def write_status(self):
        """Writes information about the current state of the deposition simulation"""
        status = {
            "last_updated": dt.now(),
            "iteration_number": self.iteration_number,
            "num_sequential_failures": self.num_sequential_failures,
            "pickle_location": self.pickle_location
        }
        io.write_yaml(Deposition.status_filename, status)

    def initial_setup(self):
        """
        Sets up the initial state of simulation, creates required directories.
        Only runs no "status.yaml" file is found (self.iteration_number is None).

        :return:
        """
        if self.iteration_number is None:
            self.iteration_number = 1
            self.num_sequential_failures = 0
            self.pickle_location = "initial_positions.pickle"
            coordinates, elements, _ = io.read_xyz(self.settings["substrate_xyz_file"])
            io.write_state(coordinates, elements, velocities=None, pickle_location=self.pickle_location)
            io.make_directories((Deposition.working_directory,
                                 Deposition.success_directory,
                                 Deposition.failure_directory))
            self.write_status()

    def run_loop(self):
        self.initial_setup()
        max_iterations = self.settings["maximum_total_iterations"]
        max_failures = self.settings["maximum_sequential_failures"]

        while (self.iteration_number <= max_iterations) and (self.num_sequential_failures <= max_failures):
            iteration = Iteration.Iteration(self.driver, self.settings, self.iteration_number, self.pickle_location)
            success, self.pickle_location = iteration.run()
            if success:
                self.num_sequential_failures = 0
            else:
                self.num_sequential_failures += 1
            self.iteration_number += 1
            self.write_status()

        return 0
