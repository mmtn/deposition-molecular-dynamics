import logging
import os
import shutil
import subprocess
from string import Template

from src import io, new_atoms


class Iteration:
    def __init__(self, driver, inputs, command_prefix):
        self.driver = driver
        self.inputs = inputs
        self.command_prefix = command_prefix
        self.iteration_number, _, self.pickle_location = io.read_status()
        self.working_directory = "current"  # TODO: make this an optional input
        self.deposition_filename = f"{self.working_directory}/deposition{self.iteration_number:03d}"
        self.relaxation_filename = f"{self.working_directory}/relaxation{self.iteration_number:03d}"
        self.success = False

    def run(self):
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
        coordinates, elements, velocities = new_atoms.add(self.inputs, coordinates, elements, velocities)
        self.driver.write_inputs(self.deposition_filename, coordinates, elements, velocities)
        self.call_process(self.deposition_filename)
        coordinates, elements, velocities = self.driver.read_outputs(self.deposition_filename)
        io.write_state(coordinates, elements, velocities=None, pickle_location=f"{self.deposition_filename}.pickle")

    def finish(self):
        self.check_outcome()
        if self.success:
            destination = "iterations"
            self.pickle_location = f"iterations/{self.iteration_number:03d}/deposition{self.iteration_number:03d}.pickle"
        else:
            destination = "failed"
        destination_directory = f"{destination}/{self.iteration_number:03d}/"
        shutil.copytree(self.working_directory, destination_directory)
        shutil.rmtree(self.working_directory)
        os.mkdir(self.working_directory)
        self.driver.after_calculation(self.working_directory, destination_directory)
        if self.success and self.iteration_number == 1:
            shutil.move("initial_positions.pickle", destination_directory)

    def call_process(self, filename):
        command_settings = dict()
        command_settings["prefix"] = self.command_prefix
        command_settings["binary"] = self.driver.binary
        command_settings["input_file"] = f"{filename}.input"
        command_settings["output_file"] = f"{filename}.output"
        command_template = Template(self.driver.command_syntax)
        command = command_template.substitute(command_settings)
        logging.info(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)

    def check_outcome(self):
        # TODO: implement routines to check validity of calculation outputs (driver specific?)
        self.success = True
