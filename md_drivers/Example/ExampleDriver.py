import os
from src import io


class ExampleDriver:
    def __init__(self):
        """
        Any constants required for the software can be set in this function.
        """
        self.path = os.path.dirname(os.path.realpath(__file__))

        # Required variables
        self.name = "Example"
        self.binary = "example"
        self.command_syntax = "${prefix} ${binary} < ${input_file} > ${output_file}"

        # Additional variables
        self.input_template = f"{self.path}/ExampleInputTemplate.txt"

        # Function to run at set up time
        self.set_environment_variables()

    def set_environment_variables(self):
        # os.putenv("VARIABLE_NAME", "value")
        pass

    def after_calculation(self):
        """ Any required post-processing of the calculation output can be done here """
        pass

    def write_inputs(self, filename, coordinates, elements, velocities):
        """
        Generate all required input files for each iteration from the data for N atoms. This function should produce
        inputs for the "relaxation" calculation when velocities=None.

        :param filename: the basename of the input files, e.g. relaxation003
        :param coordinates: Nx3 array of xyz location per atom
        :param elements: Nx1 list of element labels per atom
        :param velocities: Nx3 array of xyz velocities per atom
        """
        pass

    def read_outputs(self, filename):
        """
        Returns the state of the system at the end of the calculation for N atoms as specified by reading the output
        files from the calculation. Functions in io.py may be helpful here, e.g. io.read_xyz(xyz_file)

        :param filename: the basename of the input files, e.g. relaxation003
        :return coordinates: Nx3 array of xyz location per atom
        :return elements: Nx1 list of element labels per atom
        :return velocities: Nx3 array of xyz velocities per atom
        """
        coordinates, elements, num_atoms = io.read_xyz(f"{filename}.xyz")
        velocities = None
        return coordinates, elements, velocities
