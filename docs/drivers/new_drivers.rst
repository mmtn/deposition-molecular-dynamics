.. _new_drivers:

Writing a new molecular dynamics driver
=======================================

This is a guide to writing a Python class which will function as a bridge between the deposition code and your chosen
molecular dynamics software. At any point feel free to examine the source code of the drivers provided for
:class:`LAMMPS <deposition.drivers.LAMMPSDriver>` and :class:`GULP <deposition.drivers.GULPDriver>` as any new driver
will need to take on a very similar form. A :class:`template <deposition.drivers.TemplateDriver.TemplateDriver>` to
build on is provided (follow the link then click "source").

The addition of a new molecular dynamics driver involves completing the following tasks:

- make a copy of `drivers/TemplateDriver.py` and rename it according to the name of the molecular dynamics software
- change the `name` attribute in the driver to match the molecular dynamics software
- write implementations of `write_inputs` and `read_outputs` specific to the software
- (optionally) define software specific inputs in `schema_dictionary`

As with other drivers, an input template must be used which is compatible with the molecular dynamics driver and
has a keyword which allows for the simulation time to vary between the relaxation and deposition stages of each
iteration.

.. note::

   The `${filename}` variable is reserved and must be placed in the template for the names of any input and output
   files. For example, in the LAMMPS input template the final state is written using the command
   `write_data ${filename}.output_data`.

Listed below are the attributes and methods which are inherited from the
:class:`MolecularDynamicsDriver <deposition.drivers.MolecularDynamicsDriver.MolecularDynamicsDriver>` class. Each
may be specified for the individual driver. Additional attributes and methods can also be defined.

Attributes
----------

`name` (required)
^^^^^^^^^^^^^^^^^

The name to use when referencing this molecular dynamics driver. The driver will be initialised when the name in the
input settings matches this variable.

`schema_dictionary` (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A dictionary listing the names and types of any additional inputs required by the molecular dynamics software. Keywords
listed here can then be set as `driver_settings` in the YAML file containing the deposition settings. The dictionary is
used to construct a `Schema <https://github.com/keleshev/schema>`_ which the input settings are validated against.

`command` (optional)
^^^^^^^^^^^^^^^^^^^^

A template specifying how to call the molecular dynamics software at the command line. The default command is
`"${prefix} ${binary} < ${input_file} > ${output_file}"`.


Methods
-------

A driver class must provide two main methods: `write_inputs` and `read_outputs`. They must be defined as specified
here. They are called from the :meth:`relaxation <deposition.Iteration.relaxation>` and
:meth:`deposition <deposition.Iteration.deposition>` methods of the :class:`Iteration <deposition.Iteration>` class.


`write_inputs` (required)
^^^^^^^^^^^^^^^^^^^^^^^^^

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


`read_outputs` (required)
^^^^^^^^^^^^^^^^^^^^^^^^^

This function can (but need not be) implemented as a static method. This function must read data produced by the
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

