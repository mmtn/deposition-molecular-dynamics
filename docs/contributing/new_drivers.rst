.. _new_drivers:

Writing a new molecular dynamics driver
=======================================

This is a guide to writing a Python class which will function as a bridge between the deposition code and your chosen
molecular dynamics software. At any point feel free to examine the source code of the drivers provided for
:ref:`LAMMPS <driver_LAMMPSDriver>` and :ref:`GULP <driver_GULPDriver>` as any new driver
will need to take on a very similar form. A :ref:`template <driver_TemplateDriver>` to
build on is provided (follow the link then click "[source]").

The addition of a new molecular dynamics driver involves completing the following tasks:

- make a copy of `drivers/template_driver.py` and rename it according to the name of the molecular dynamics software
- rename the class from `TemplateDriver` to the chosen name
- add a value to the Enum in `drivers/driver_enums.py` referring to the new driver class
- write implementations of `write_inputs` and `read_outputs` specific to the software

Optionally, you may also:

    - define software specific inputs in `schema_dict`
    - set up internal keywords using `reserved_keywords`
    - specify a custom syntax for running the software with `command`

As with other drivers, an input template must be used which is compatible with the molecular dynamics driver and
has a keyword which allows for the simulation time to vary between the relaxation and deposition stages of each
iteration.

.. note::

   The `${filename}` variable is reserved and must be placed in the template for the names of any input and output
   files. For example, in the LAMMPS input template the final state is written using the command
   `write_data ${filename}.output_data`.


Attributes
----------

Variables associated with the class. The template file has some examples of the values these might have.

`schema_dict`
^^^^^^^^^^^^^

A dictionary listing the names and types of any additional inputs required by the molecular dynamics software. Keywords
listed here can then be set as `driver_settings` in the YAML file containing the deposition settings. The dictionary is
used to construct a `Schema <https://github.com/keleshev/schema>`_ which the input settings are validated against.

`reserved_keywords`
^^^^^^^^^^^^^^^^^^^

Any variable to be calculated internal to the class and substituted into the input template file. For example, the
keyword `simulation_time` is in this list for the template class. This value is then set depending on whether the
iteration is at the relaxation or deposition stage. This system avoids duplication of keywords as by including the
keyword in this list, it is unable to be used as a regular template variable.

`command`
^^^^^^^^^

A template specifying how to call the molecular dynamics software at the command line. The default command is
`"${prefix} ${binary} ${arguments} < ${input_file} > ${output_file}"`. The values in the command are derived from:

    - prefix: settings > `command_prefix`
    - binary: driver settings > `path_to_binary`
    - arguments: driver settings > `command_line_args`
    - input_file: depositionXYZ.input or relaxationXYZ.input
    - output_file: depositionXYZ.output or relaxationXYZ.output

where XYZ is the iteration number padded to three digits.

Methods
-------

A driver class must provide two main methods: `write_inputs` and `read_outputs`. They must be defined as specified
here. They are called from the :meth:`relaxation <deposition.iteration.Iteration.relaxation>` and
:meth:`deposition <deposition.iteration.Iteration.deposition>` methods of the
:class:`Iteration <deposition.iteration.Iteration>` class.


`write_inputs`
^^^^^^^^^^^^^^

This function must accept data about the system and use it to write the input files for the next stage of the
calculation. Velocities should be written when setting up the "deposition" stage to maintain continuity between the two
parts of each iteration. Velocities can be ignored in the "relaxation" stage.

The function must accept variables of the following types in this order:

- filename (str): basename to use for input files
- coordinates (np.array): coordinate data
- elements (list): atomic species data
- velocities (np.array): velocity data
- iteration_stage (str): either "relaxation" or "deposition"

A much simplified template is shown here::

    def write_inputs(filename, coordinates, elements, velocities, iteration_stage):
        io.write_file_using_template(f"{filename}.input", self.settings["path_to_input_template"], self.settings)
        write_coordinates(f"{filename}.input", coordinates)
        write_elements(f"{filename}.input", elements)
        if iteration_stage ^^ "deposition":
            write_velocities(f"{filename}.input", velocities)


`read_outputs`
^^^^^^^^^^^^^^

This function should be implemented as a static method. It must read data produced by the
molecular dynamics software and return it as a tuple with the following order and formats:

- coordinates (np.array): coordinate data
- elements (list): atomic species data
- velocities (np.array): velocity data

A much simplified template is shown here::

    @staticmethod
    def read_outputs(filename):
        coordinates = read_coordinates(f"{filename}.output")
        elements = read_elements(f"{filename}.output")
        velocities = read_velocities(f"{filename}.output")
        return coordinates, elements, velocities

