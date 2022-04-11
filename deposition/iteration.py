import logging
import os
import shutil
import subprocess
from string import Template

from deposition.state import State
from deposition.enums import DirectoriesEnum
from deposition import postprocessing, randomisation


class Iteration:
    """
    The `Iteration` class represents one cycle of relaxing the system before
    depositing an atom/molecule as specified
    by the input settings.

    Each iteration consists of the following steps:

    - relaxation: simulation at the specified temperature to equilibrate the system
    - deposition: simulation of the introduction of a new atom/molecule
    - finalisation: the final simulation state is analysed against various criteria
    and the data is stored

    This class is also responsible for using the `subprocess` package to run the
    molecular dynamics software.
    """

    def __init__(self, driver, settings, status):
        self.driver = driver
        self.settings = settings
        self.iteration_number = status.iteration_number
        self.pickle_location = status.pickle_location
        self.deposition_filename = os.path.join(
            DirectoriesEnum.WORKING.value,
            f"deposition{self.iteration_number:04d}",
        )
        self.relaxation_filename = os.path.join(
            DirectoriesEnum.WORKING.value,
            f"relaxation{self.iteration_number:04d}",
        )
        self.success = False
        self.state = State.read_state(self.pickle_location)

    def run(self):
        """
        Runs one iteration of relaxation, deposition, and finalisation. Returns to
        Deposition the success or failure of this iteration, and the location of
        the saved data from which to start the next iteration.

        Returns:
             success, pickle_location (tuple)
                - success (bool): whether the iteration passes the structural analyses
                - pickle_location (path): where the resulting data has been saved
        """
        logging.info(f"starting iteration {self.iteration_number}")
        self.relaxation()
        self.deposition()
        self.run_postprocessing()
        self.finalisation()
        return self.success, self.pickle_location

    def relaxation(self):
        """Runs the relaxation phase of the iteration."""
        self.driver.write_inputs(self.relaxation_filename, self.state)
        self.call_process(self.relaxation_filename)
        self.state = self.driver.read_outputs(self.relaxation_filename)

    def deposition(self):
        """Runs the deposition phase of the iteration including the random addition
        of new atoms/molecules."""
        self.state = randomisation.new_coordinates_and_velocities(
            self.settings,
            self.state,
            self.driver.simulation_cell,
            self.driver.settings["velocity_scaling_from_metres_per_second"],
        )
        self.driver.write_inputs(self.deposition_filename, self.state)
        self.call_process(self.deposition_filename)
        self.state = self.driver.read_outputs(self.deposition_filename)

    def finalisation(self):
        """Finalises the iteration by moving the data to the appropriate directory"""
        self.state.write(f"{self.deposition_filename}.pickle", include_velocities=False)
        if self.success:
            destination_directory = os.path.join(
                DirectoriesEnum.SUCCESS.value, f"{self.iteration_number:03d}/"
            )
            self.pickle_location = os.path.join(
                destination_directory, f"deposition{self.iteration_number:03d}.pickle"
            )
        else:
            destination_directory = os.path.join(
                DirectoriesEnum.FAILED.value, f"{self.iteration_number:03d}/"
            )
        logging.info(
            f"moving data for iteration {self.iteration_number} to {destination_directory}"
        )
        shutil.copytree(DirectoriesEnum.WORKING.value, destination_directory)
        shutil.rmtree(DirectoriesEnum.WORKING.value)
        os.mkdir(DirectoriesEnum.WORKING.value)

    def run_postprocessing(self):
        """Runs postprocessing routines on the final state of the deposition phase."""
        if self.settings.postprocessing is None:
            self.success = True
            return

        logging.info("running post processing")

        try:
            for name, args in self.settings.postprocessing.items():
                logging.info(f"- {name}")
                self.state = postprocessing.run(
                    name, self.state, self.settings.simulation_cell, args
                )
            self.success = True

        except RuntimeWarning as warning:
            logging.warning("post-processing check failed")
            logging.warning(warning)
            if self.settings.strict_postprocessing:
                raise RuntimeError(warning)
            self.success = False

    def call_process(self, filename):
        """Run the molecular dynamics software for this phase of the iteration."""
        command_template = Template(self.driver.command)
        command_template_values = dict()
        command_template_values["prefix"] = self.settings.command_prefix
        command_template_values["binary"] = self.driver.binary
        command_template_values["arguments"] = self.driver.settings["command_line_args"]
        command_template_values["input_file"] = f"{filename}.input"
        command_template_values["output_file"] = f"{filename}.output"
        command = command_template.substitute(command_template_values)
        logging.info(f"running: {command}")
        subprocess.run(command, shell=True, check=True)
