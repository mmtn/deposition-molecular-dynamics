import os

from schema import Or

from deposition import io
from deposition.drivers.MolecularDynamicsDriver import MolecularDynamicsDriver


class TemplateDriver(MolecularDynamicsDriver):
    """
    Template to help with writing new MolecularDynamicsDriver classes
    """

    name = "Template"

    schema_dict = {
        "atomic_masses": list,
        "path_to_potential": os.path.exists,
        "thermostat_parameter": Or(float, int),
    }

    reserved_keywords = [
        "simulation_time",
    ]

    command = "${prefix} ${binary} < ${input_file} > ${output_file}"

    def __init__(self, driver_settings, simulation_cell):
        super().__init__(
            driver_settings,
            simulation_cell,
            command=self.command,
            schema_dict=self.schema_dict,
            reserved_keywords=self.reserved_keywords
        )

    def write_inputs(self, filename, coordinates, elements, velocities, iteration_stage):
        def write_coordinates(file, coordinates):
            pass

        def write_elements(file, elements):
            pass

        def write_velocities(file, elements):
            pass

        io.write_file_using_template(f"{filename}.input", self.settings["path_to_input_template"], self.settings)
        write_coordinates(f"{filename}.input", coordinates)
        write_elements(f"{filename}.input", elements)
        if iteration_stage == "deposition":
            write_velocities(f"{filename}.input", velocities)

    @staticmethod
    def read_outputs(filename):
        def read_coordinates(file):
            pass

        def read_elements(file):
            pass

        def read_velocities(file):
            pass

        coordinates = read_coordinates(f"{filename}.output")
        elements = read_elements(f"{filename}.output")
        velocities = read_velocities(f"{filename}.output")
        return coordinates, elements, velocities
