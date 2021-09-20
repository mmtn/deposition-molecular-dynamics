import logging
import yaml
from datetime import datetime as dt
from deposition import Iteration, io, utils


class Deposition:
    _status_filename = "status.yaml"
    _working_dir = "current"
    _success_dir = "iterations"
    _failure_dir = "failed"

    def __init__(self, settings: dict):
        self.settings = settings
        io.start_logging(self.settings["log_filename"])
        self.simulation_cell = utils.get_simulation_cell(settings["simulation_cell"])
        self.driver = utils.get_molecular_dynamics_driver(
            self.settings["driver_settings"],
            self.simulation_cell,
            self.settings["deposition_time_picoseconds"],
            self.settings["relaxation_time_picoseconds"]
        )
        self.iteration_number, self.num_sequential_failures, self.pickle_location = self.read_status()

    def initial_setup(self):
        """
        Sets up the initial state of simulation and creates the required directories.
        Note that this function only runs when no status.yaml file is found (self.iteration_number is None).
        """
        if self.iteration_number is None:
            self.iteration_number = 1
            self.num_sequential_failures = 0
            self.pickle_location = "initial_positions.pickle"
            coordinates, elements, _ = io.read_xyz(self.settings["substrate_xyz_file"])
            io.write_state(coordinates, elements, velocities=None, pickle_location=self.pickle_location)
            io.make_directories((Deposition._working_dir, Deposition._success_dir, Deposition._failure_dir))
            self.write_status()

    def run(self):
        self.initial_setup()
        max_iterations = self.settings["maximum_total_iterations"]
        max_failures = self.settings["maximum_sequential_failures"]

        while (self.iteration_number <= max_iterations) and (self.num_sequential_failures <= max_failures):
            iteration = Iteration(self.driver, self.settings, self.iteration_number, self.pickle_location)
            success, self.pickle_location = iteration.run()
            if success:
                self.num_sequential_failures = 0
            else:
                self.num_sequential_failures += 1
            self.iteration_number += 1
            self.write_status()

        return 0

    @staticmethod
    def read_status():
        """
        Reads the current iteration number, number of sequential failures, and the most recent saved state of the
        deposition simulation from status.yaml.
        """
        try:
            with open(Deposition._status_filename) as file:
                status = yaml.safe_load(file)
            iteration_number = int(status["iteration_number"])
            num_sequential_failures = int(status["num_sequential_failures"])
            pickle_location = status["pickle_location"]
            return iteration_number, num_sequential_failures, pickle_location
        except FileNotFoundError:
            logging.info("no status.yaml file found")
            return None, None, None

    def write_status(self):
        """
        Writes the current time, current iteration number, number of sequential failures, and the most recent saved
        state of the deposition simulation to status.yaml.
        """
        status = {
            "last_updated": dt.now(),
            "iteration_number": self.iteration_number,
            "num_sequential_failures": self.num_sequential_failures,
            "pickle_location": self.pickle_location
        }
        with open(Deposition._status_filename, "w") as file:
            yaml.dump(status, file)
