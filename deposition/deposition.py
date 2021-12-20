import logging
from datetime import datetime as dt

import yaml

from deposition import io, utils
from deposition.iteration import Iteration
from deposition.settings import Settings
from deposition.state import State


class Deposition:
    """
    The Deposition class controls the overall state of the calculation.

    This is the primary object which manages the simulation. It is responsible for
    creating the directories where calculation data will be kept, transferring data
    between iterations, and keeping track of how many iterations have been performed and
    how many have failed. The Deposition class will also initialise a molecular dynamics
    driver.
    """

    _status_file = "status.yaml"

    def __init__(self, settings_dict):
        """
        Initialise the simulation cell and molecular dynamics driver. Read the status
        of the deposition calculation from `status.yaml` if it is present.

        Arguments:
            settings_dict (dict): deposition settings (read with
            `deposition.io.read_settings_from_file()`)
        """
        self.settings = Settings(settings_dict)
        io.start_logging(self.settings.log_filename)
        self.status = self.read_status()
        self.driver = utils.get_molecular_dynamics_driver(
            self.settings.driver_settings,
            self.settings.simulation_cell,
            self.settings.deposition_time,
            self.settings.relaxation_time,
        )

    def initial_setup(self):
        """
        Sets simulation parameters to their initial state and creates the required
        directories. Note that this function only runs when no `status.yaml` file is
        found in the current directory.
        """
        self.status = Status(
            iteration_number=1,
            sequential_failures=0,
            total_failures=0,
            pickle_location="initial_positions.pickle",
        )
        state = io.read_xyz(self.settings.substrate_xyz_file)
        io.write_state(state, self.status.pickle_location, include_velocities=False)
        io.make_directories(tuple(io.directories.values()))
        self.write_status()

    def run(self):
        """
        Executes the main deposition loop using the :class:`Iteration` class.

        Returns:
            exit_code (int): a code relating to the reason for the termination of the
        """
        if self.status is None:
            self.initial_setup()
        max_iterations = self.settings.max_total_iterations
        max_failures = self.settings.max_sequential_failures

        while True:
            iteration = Iteration(
                self.driver,
                self.settings,
                self.status.iteration_number,
                self.status.pickle_location,
            )
            success, self.status.pickle_location = iteration.run()
            if success:
                self.status.sequential_failures = 0
            else:
                self.status.sequential_failures += 1
                self.status.total_failures += 1
            self.status.iteration_number += 1
            self.write_status()

            if self.status.iteration_number > max_iterations:
                exit_code = 0
                return 0  # exceeded maximum iterations

            elif self.status.sequential_failures > max_failures:
                return 1  # exceeded maximum failures

    @staticmethod
    def read_status():
        """
        Reads the current iteration number, number of sequential failures, and the
        most recent saved state of the
        deposition simulation from `status.yaml`.
        """
        try:
            with open(Deposition._status_file) as file:
                status = yaml.safe_load(file)
            return Status(
                int(status["iteration_number"]),
                int(status["sequential_failures"]),
                int(status["total_failures"]),
                status["pickle_location"],
            )
        except FileNotFoundError:
            logging.info(f"no {Deposition._status_file} file found")
            return None

    def write_status(self):
        """
        Writes the current time, current iteration number, number of sequential
        failures, and the most recent saved state of the deposition simulation to
        `status.yaml`.
        """
        status = {
            "last_updated": dt.now(),
            "iteration_number": self.status.iteration_number,
            "sequential_failures": self.status.sequential_failures,
            "total_failures": self.status.total_failures,
            "pickle_location": self.status.pickle_location,
        }
        with open(Deposition._status_file, "w") as file:
            yaml.dump(status, file)


class Status:
    """Track the status of the deposition calculation"""

    def __init__(
        self,
        iteration_number,
        sequential_failures,
        total_failures,
        pickle_location,
    ):
        self.iteration_number = iteration_number
        self.sequential_failures = sequential_failures
        self.total_failures = total_failures
        self.pickle_location = pickle_location
