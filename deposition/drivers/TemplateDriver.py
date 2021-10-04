from schema import Optional, Use

from deposition import io, schema_validation
from deposition.drivers.MolecularDynamicsDriver import MolecularDynamicsDriver


class TemplateDriver(MolecularDynamicsDriver):

    name = "Template"

    schema_dictionary = {
        Optional("custom_keyword"): Use(schema_validation.reserved_keyword),
    }

    command = "${prefix} ${binary} < ${input_file} > ${output_file}"

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
