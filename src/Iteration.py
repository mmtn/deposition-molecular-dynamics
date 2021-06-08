import logging
import os
import shutil
import subprocess
from string import Template

from src import io, randomise_deposited_atoms, structural_analysis, Deposition


class Iteration:
    def __init__(self, driver, settings, iteration_number, pickle_location):
        self.driver = driver
        self.settings = settings
        self.iteration_number = iteration_number
        self.pickle_location = pickle_location
        self.deposition_filename = f"{Deposition.Deposition.working_directory}/deposition{self.iteration_number:03d}"
        self.relaxation_filename = f"{Deposition.Deposition.working_directory}/relaxation{self.iteration_number:03d}"
        self.success = False

    def run(self):
        logging.info(f"starting iteration {self.iteration_number}")
        self.relaxation()
        self.deposition()
        self.finish()
        return self.success, self.pickle_location

    def relaxation(self):
        coordinates, elements, velocities = io.read_state(self.pickle_location)
        self.driver.write_inputs(self.relaxation_filename, coordinates, elements, velocities, "relaxation")
        self.call_process(self.relaxation_filename)
        coordinates, elements, velocities = self.driver.read_outputs(self.relaxation_filename)
        io.write_state(coordinates, elements, velocities, pickle_location=f"{self.relaxation_filename}.pickle")

    def deposition(self):
        coordinates, elements, velocities = io.read_state(f"{self.relaxation_filename}.pickle")
        coordinates, elements, velocities = randomise_deposited_atoms.append_new_coordinates_and_velocities(
            self.settings,
            coordinates,
            elements,
            velocities,
            self.driver.simulation_cell,
            self.driver.settings["velocity_scaling_from_metres_per_second"]
        )
        self.driver.write_inputs(self.deposition_filename, coordinates, elements, velocities, "deposition")
        self.call_process(self.deposition_filename)
        coordinates, elements, velocities = self.driver.read_outputs(self.deposition_filename)
        self.check_outcome(coordinates, elements)
        io.write_state(coordinates, elements, velocities=None, pickle_location=f"{self.deposition_filename}.pickle")

    def finish(self):
        if not self.success:
            destination_directory = f"{Deposition.Deposition.failure_directory}/{self.iteration_number:03d}/"
        else:
            destination_directory = f"{Deposition.Deposition.success_directory}/{self.iteration_number:03d}/"
            self.pickle_location = f"{destination_directory}/deposition{self.iteration_number:03d}.pickle"
        logging.info(f"moving data for iteration {self.iteration_number} to {destination_directory}")
        shutil.copytree(Deposition.Deposition.working_directory, destination_directory)
        shutil.rmtree(Deposition.Deposition.working_directory)
        os.mkdir(Deposition.Deposition.working_directory)

    def call_process(self, filename):
        command_template = Template(self.driver.command_syntax)
        command_template_values = dict()
        command_template_values["prefix"] = self.settings["command_prefix"]
        command_template_values["binary"] = self.driver.binary
        command_template_values["input_file"] = f"{filename}.input"
        command_template_values["output_file"] = f"{filename}.output"
        command = command_template.substitute(command_template_values)
        logging.info(f"running: {command}")
        subprocess.run(command, shell=True, check=True)

    def check_outcome(self, coordinates, elements):
        logging.info("running structural analysis to check outcome")
        try:
            structural_analysis.check_min_neighbours(self.settings, self.driver.simulation_cell, coordinates)
            structural_analysis.check_bonding_at_lower_interface(self.settings, self.driver.simulation_cell,
                                                                 coordinates, elements)
            self.success = True
        except RuntimeWarning as warning:
            logging.warning(warning)
            logging.warning("post-processing check failed")
            self.success = False
