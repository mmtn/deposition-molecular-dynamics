.. _new_drivers:

Writing a new molecular dynamics driver
=======================================

This is a guide to writing a Python class which will function as a bridge between the deposition code and your chosen
molecular dynamics software. At any point feel free to examine the source code of the drivers provided for
:class:`LAMMPS <deposition.drivers.LAMMPSDriver>` and :class:`GULP <deposition.drivers.GULPDriver>` as any new driver
will need to take on a very similar form. A :class:`template <deposition.drivers.TemplateDriver.TemplateDriver>` to
build on is provided (follow the link then click "source").

At a bare minimum, the new driver class must have a name attribute, a `write_inputs` method, and a `read_outputs`
method.

Variables
---------

`name` (required)

The name to use when referencing this molecular dynamics driver. The driver will be initialised when the driver name in
the input settings matches this name.

`schema_dictionary` (optional)

A dictionary listing the names and types of any additional inputs required by the molecular dynamics software. Keywords
listed here can then be set as `driver_settings` in the YAML file containing the deposition settings.

`command` (optional)

A template specifying how to call the molecular dynamics software at the command line. The default command is
`"${prefix} ${binary} < ${input_file} > ${output_file}"`.


Methods
-------

A driver class **must** provide two main methods: `write_inputs` and `read_outputs`. They must be defined as specified
here. They are called from the :meth:`relaxation <deposition.Iteration.relaxation>` and
:meth:`deposition <deposition.Iteration.deposition>` methods of the :class:`Iteration <deposition.Iteration>` class.


write_inputs
^^^^^^^^^^^^

This function must accept data about the system and use it to write the input files for the next stage of the
calculation. Velocities should be written when setting up the "deposition" stage to maintain continuity between the two
parts of each iteration. Velocities can be ignored in the "relaxation" stage.

The function must accept variables of the following types:

- filename (str): basename to use for input files
- coordinates (np.array): coordinate data
- elements (list): atomic species data
- velocities (np.array): velocity data
- iteration_stage (str): either "relaxation" or "deposition"

A much simplified template is shown here::

    def write_inputs(filename, coordinates, elements, velocities, iteration_stage):
        io.write_file_using_template(input_filename, self.settings["path_to_input_template"], self.settings)
        write_coordinates(f"{filename}.input", coordinates)
        write_elements(f"{filename}.input", elements)
        if iteration_stage == "deposition":
            write_velocities(f"{filename}.input", velocities)

read_outputs
^^^^^^^^^^^^

This function can (but need not be) implemented as a static method. This function must read data produced by the
molecular dynamics software and return it as a tuple with the following order and formats:

- coordinates (np.array): coordinate data
- elements (list): atomic species data
- velocities (np.array): velocity data

A much simplified template is shown here::

    @staticmethod
    def read_outputs(filename):
        coordinates = read_your_coordinate_data()
        elements = read_your_element_data()
        velocities = read_your_velocity_data()
        return coordinates, elements, velocities

