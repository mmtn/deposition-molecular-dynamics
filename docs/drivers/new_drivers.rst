.. _new_drivers:

Writing a new molecular dynamics driver
=======================================

Variables
---------

`name` (required)

The name to use when referencing this molecular dynamics driver. The driver will be initialised when the driver name in
the input settings matches this name.

`schema_dictionary` (optional)

A dictionary listing the names and types of any additional inputs required by the molecular dynamics software.

`command` (optional)

Template specifying how to call the molecular dynamics software at the command line. The default command is
`"${prefix} ${binary} < ${input_file} > ${output_file}"`.

Methods
-------

A driver class **must** provide two main methods: `write_inputs` and `read_outputs`. They must be defined as specified
here.

write_inputs
^^^^^^^^^^^^

`write_inputs(filename, coordinates, elements, velocities, iteration_stage)`

This function must accept data about the system and use it to write the input files for the next stage of the
calculation. Velocities should be written when setting up the "deposition" stage to maintain continuity between the two
parts of each iteration. Velocities can be ignored in the "relaxation" stage.

The function must accept variable of the following types:

- filename: `str`, name to use for input files
- coordinates: `np.array`?, coordinate data
- elements: `list`, atomic species data
- velocities: `np.array`?, velocity data
- iteration_stage: `str`, either "relaxation" or "deposition"

read_outputs
^^^^^^^^^^^^

`read_outputs(filename)`

This function must read data produced by the molecular dynamics software and return it in the following order and
format:

- coordinates: `np.array`?, coordinate data
- elements: `list`, atomic species data
- velocities: `np.array`?, velocity data
