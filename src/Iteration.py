import logging
import os
import shutil
import subprocess
from string import Template

from src import io, atoms, structural_analysis


class Iteration:
    def __init__(self, driver, settings, iteration_number, pickle_location):
        self.driver = driver
        self.settings = settings
        self.iteration_number = iteration_number
        self.pickle_location = pickle_location
        self.working_directory = "current"
        self.deposition_filename = f"{self.working_directory}/deposition{self.iteration_number:03d}"
        self.relaxation_filename = f"{self.working_directory}/relaxation{self.iteration_number:03d}"
        self.success = False

    def run(self):
        logging.info(f"starting iteration {self.iteration_number}")
        self.relaxation()
        self.deposition()
        self.finish()
        return self.success, self.pickle_location

    def relaxation(self):
        coordinates, elements, velocities = io.read_state(self.pickle_location)
        self.driver.write_inputs(self.relaxation_filename, coordinates, elements, velocities)
        self.call_process(self.relaxation_filename)
        coordinates, elements, velocities = self.driver.read_outputs(self.relaxation_filename)
        io.write_state(coordinates, elements, velocities, pickle_location=f"{self.relaxation_filename}.pickle")

    def deposition(self):
        coordinates, elements, velocities = io.read_state(f"{self.relaxation_filename}.pickle")
        coordinates, elements, velocities = atoms.generate(self.settings, self.driver, coordinates, elements, velocities)
        self.driver.write_inputs(self.deposition_filename, coordinates, elements, velocities)
        self.call_process(self.deposition_filename)
        coordinates, elements, velocities = self.driver.read_outputs(self.deposition_filename)
        self.check_outcome(coordinates, elements)
        io.write_state(coordinates, elements, velocities=None, pickle_location=f"{self.deposition_filename}.pickle")

    def finish(self):
        if self.success:
            destination = "iterations"
            self.pickle_location = f"iterations/{self.iteration_number:03d}/deposition{self.iteration_number:03d}.pickle"
        else:
            destination = "failed"
        destination_directory = f"{destination}/{self.iteration_number:03d}/"
        logging.info(f"moving data for iteration {self.iteration_number} to {destination_directory}")
        shutil.copytree(self.working_directory, destination_directory)
        shutil.rmtree(self.working_directory)
        os.mkdir(self.working_directory)
        self.driver.after_calculation(self.working_directory, destination_directory)
        if self.success and self.iteration_number == 1:
            shutil.move("initial_positions.pickle", destination_directory)

    def call_process(self, filename):
        command_settings = dict()
        command_settings["prefix"] = self.settings["command_prefix"]
        command_settings["binary"] = self.driver.binary
        command_settings["input_file"] = f"{filename}.input"
        command_settings["output_file"] = f"{filename}.output"
        command_template = Template(self.driver.command_syntax)
        command = command_template.substitute(command_settings)
        logging.info(f"running: {command}")
        subprocess.run(command, shell=True, check=True)

    def check_outcome(self, coordinates, elements):
        logging.info("running structural analysis to check outcome")
        try:
            structural_analysis.check_min_neighbours(self.settings, self.driver.substrate, coordinates)
            structural_analysis.check_bonding_at_lower_interface(self.settings, self.driver.substrate, coordinates, elements)
            self.success = True
        except RuntimeWarning as warning:
            logging.warning(warning)
            logging.warning("post-processing check failed")
            self.success = False
