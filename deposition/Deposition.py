import logging
from datetime import datetime as dt

import yaml

from deposition import io, utils
from deposition.Iteration import Iteration


class Deposition:
    """
    The Deposition class controls the overall state of the calculation.

    This is the primary object which manages the simulation. It is responsible for creating the directories where
    calculation data will be kept, transferring data between iterations, and keeping track of how many iterations have
    been performed and how many have failed. The  Deposition class will also initialise a molecular dynamics driver.
    """

    _status_file = "status.yaml"

    def __init__(self, settings):
        """
        Initialise the simulation cell and molecular dynamics driver. Read the status of the deposition calculation from
        `status.yaml` if it is present.

        Arguments:
            settings (dict): deposition settings (read with `deposition.io.read_settings_from_file()`)
        """
        self.settings = settings
        io.start_logging(self.settings["log_filename"])
        self.driver = utils.get_molecular_dynamics_driver(
            self.settings["driver_settings"],
            self.settings["simulation_cell"],
            self.settings["deposition_time_picoseconds"],
            self.settings["relaxation_time_picoseconds"]
        )
        self.iteration_number, self.sequential_failures, self.total_failures, self.pickle_location = self.read_status()

    def initial_setup(self):
        """
        Sets simulation parameters to their initial state and creates the required directories. Note that this function
        only runs when no `status.yaml` file is found in the current directory.
        """
        self.iteration_number = 1
        self.sequential_failures = 0
        self.total_failures = 0
        self.pickle_location = "initial_positions.pickle"
        coordinates, elements, _ = io.read_xyz(self.settings["substrate_xyz_file"])
        io.write_state(coordinates, elements, velocities=None, pickle_location=self.pickle_location)
        io.make_directories(tuple(io.directories.values()))
        self.write_status()

    def run(self):
        """
        Executes the main deposition loop using the :class:`Iteration` class.

        Returns:
            exit_code (int): a code relating to the reason for the termination of the calculation
        """
        if self.iteration_number is None:
            self.initial_setup()
        max_iterations = self.settings["maximum_total_iterations"]
        max_failures = self.settings["maximum_sequential_failures"]

        while (self.iteration_number <= max_iterations) and (self.sequential_failures <= max_failures):
            iteration = Iteration(self.driver, self.settings, self.iteration_number, self.pickle_location)
            success, self.pickle_location = iteration.run()
            if success:
                self.sequential_failures = 0
            else:
                self.sequential_failures += 1
                self.total_failures += 1
            self.iteration_number += 1
            self.write_status()

        if self.iteration_number > max_iterations:  # exceeded maximum iterations
            exit_code = 0
        elif self.sequential_failures > max_failures:  # exceeded maximum failures
            exit_code = 1
        else:  # something else went wrong
            exit_code = 2

        return exit_code

    @staticmethod
    def read_status():
        """
        Reads the current iteration number, number of sequential failures, and the most recent saved state of the
        deposition simulation from `status.yaml`.
        """
        try:
            with open(Deposition._status_file) as file:
                status = yaml.safe_load(file)
            iteration_number = int(status["iteration_number"])
            sequential_failures = int(status["sequential_failures"])
            total_failures = int(status["total_failures"])
            pickle_location = status["pickle_location"]
            return iteration_number, sequential_failures, total_failures, pickle_location
        except FileNotFoundError:
            logging.info(f"no {Deposition._status_file} file found")
            return None, None, None, None

    def write_status(self):
        """
        Writes the current time, current iteration number, number of sequential failures, and the most recent saved
        state of the deposition simulation to `status.yaml`.
        """
        status = {
            "last_updated": dt.now(),
            "iteration_number": self.iteration_number,
            "sequential_failures": self.sequential_failures,
            "total_failures": self.total_failures,
            "pickle_location": self.pickle_location
        }
        with open(Deposition._status_file, "w") as file:
            yaml.dump(status, file)
