from deposition import io, utils
from deposition.enums import DirectoriesEnum
from deposition.iteration import Iteration
from deposition.settings import Settings
from deposition.status import Status


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
    _initial_positions_pickle = "initial_positions.pickle"

    def __init__(self, settings):
        """
        Initialise the simulation cell and molecular dynamics driver. Read the status
        of the deposition calculation from the status file if it is present.

        Arguments:
            settings (dict): deposition settings (read with
            `deposition.utils.read_settings_from_file()`)
        """
        self.settings = Settings(settings)
        io.start_logging(self.settings.log_filename)

        try:
            self.status = Status.from_file(self._status_file)
        except FileNotFoundError:
            self.initial_setup()

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
            pickle_location=self._initial_positions_pickle,
        )
        state = io.read_xyz(self.settings.substrate_xyz_file)
        state.write(self.status.pickle_location, include_velocities=False)
        io.make_directories(tuple([directory.value for directory in DirectoriesEnum]))
        self.status.write(self._status_file)

    def run(self):
        """
        Executes the main deposition loop using the :class:`Iteration` class.

        Returns:
            exit_code (int): a code relating to the reason for the termination of the
        """

        while True:
            iteration = Iteration(self.driver, self.settings, self.status)
            success, self.status.pickle_location = iteration.run()

            if success:
                self.status.sequential_failures = 0
            else:
                self.status.sequential_failures += 1
                self.status.total_failures += 1
            self.status.iteration_number += 1
            self.status.write(self._status_file)

            if self.status.iteration_number > self.settings.max_total_iterations:
                return 0  # exceeded maximum iterations
            if self.status.sequential_failures > self.settings.max_sequential_failures:
                return 1  # exceeded maximum failures
