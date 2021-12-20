import logging
import os
import shutil
import subprocess
from string import Template

from deposition import io, randomisation, structural_analysis


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

    def __init__(self, driver, settings, iteration_number, pickle_location):
        self.driver = driver
        self.settings = settings
        self.iteration_number = iteration_number
        self.pickle_location = pickle_location
        self.deposition_filename = os.path.join(
            io.directories["working_dir"], f"deposition{self.iteration_number:03d}"
        )
        self.relaxation_filename = os.path.join(
            io.directories["working_dir"], f"relaxation{self.iteration_number:03d}"
        )
        self.success = False

    def run(self):
        """
        Runs one iteration of relaxation, deposition, and finalisation. Returns to
        Deposition the success or failure of
        this iteration, and the location of the saved data from which to start the
        next iteration.

        Returns:
             success, pickle_location (tuple)
                - success (bool): whether the iteration passes the structural analyses
                - pickle_location (path): where the resulting data has been saved
        """
        logging.info(f"starting iteration {self.iteration_number}")
        self.relaxation()
        self.deposition()
        self.finalisation()
        return self.success, self.pickle_location

    def relaxation(self):
        """Runs the relaxation phase of the iteration."""
        state = io.read_state(self.pickle_location)
        if self.settings.to_origin_before_each_iteration:
            wrapped = structural_analysis.wrap_coordinates_in_z(
                self.driver.simulation_cell, state.coordinates
            )
            coordinates = structural_analysis.reset_to_origin(wrapped)
        self.driver.write_inputs(self.relaxation_filename, state, "relaxation")
        self.call_process(self.relaxation_filename)
        state = self.driver.read_outputs(self.relaxation_filename)
        state.write(f"{self.relaxation_filename}.pickle")

    def deposition(self):
        """Runs the deposition phase of the iteration including the random addition
        of new atoms/molecules."""
        state = io.read_state(f"{self.relaxation_filename}.pickle")
        state = randomisation.new_coordinates_and_velocities(
            self.settings,
            state,
            self.driver.simulation_cell,
            self.driver.settings["velocity_scaling_from_metres_per_second"],
        )
        self.driver.write_inputs(self.deposition_filename, state, "deposition")
        self.call_process(self.deposition_filename)
        state = self.driver.read_outputs(self.deposition_filename)
        state.write(f"{self.deposition_filename}.pickle", include_velocities=False)

    def finalisation(self):
        """Finalises the iteration by running structural analysis and moving the data
        to the appropriate directory"""
        state = io.read_state(f"{self.deposition_filename}.pickle")
        self.check_outcome(state)
        if self.success:
            destination_directory = os.path.join(
                io.directories["success_dir"], f"{self.iteration_number:03d}/"
            )
            self.pickle_location = os.path.join(
                destination_directory, f"deposition{self.iteration_number:03d}.pickle"
            )
        else:
            destination_directory = os.path.join(
                io.directories["failure_dir"], f"{self.iteration_number:03d}/"
            )
        logging.info(
            f"moving data for iteration {self.iteration_number} to "
            f"{destination_directory}"
        )
        shutil.copytree(io.directories["working_dir"], destination_directory)
        shutil.rmtree(io.directories["working_dir"])
        os.mkdir(io.directories["working_dir"])

    def call_process(self, filename):
        """
        Run the molecular dynamics software for this phase of the iteration.

        Arguments:
            filename (str): name used to label this phase of this iteration
        """
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

    def check_outcome(self, state):
        """
        Runs a structural analysis of the final state of the deposition phase.
        Currently we check whether:

        - each atom has at least the required minimum number of neighbours
        - if new atoms have bonded to the periodic copy of the substrate

        Arguments:
            state: coordinates, elements, velocities
        """
        if self.settings.deposition_type == "monatomic":
            num_deposited_atoms = self.settings.num_deposited_per_iteration
        elif self.settings.deposition_type == "molecule":
            molecule = io.read_xyz(self.settings.molecule_xyz_file)
            num_deposited_atoms = (
                len(molecule.elements) * self.settings.num_deposited_per_iteration
            )

        logging.info("running structural analyses to check outcome")
        try:
            structural_analysis.check_minimum_neighbours(
                self.settings.simulation_cell,
                state.coordinates,
                num_deposited_atoms,
                self.settings.bonding_distance_cutoff,
            )

            self.success = True
        except RuntimeWarning as warning:
            logging.warning("post-processing check failed")
            logging.warning(warning)
            if self.settings["strict_structural_analysis"]:
                raise RuntimeError(warning)
            self.success = False
