.. _contributing_postprocessing:

Adding postprocessing routines
==============================

Additional processing after each iteration may be required in certain cases. Some examples are provided in
`deposition/postprocessing.py`. New routines should be written as Python classes following the example
of the preexisting classes. These routines accept the current state of the simulation as a :ref:`State <module_state>`
object and examine or modify it before returning a :ref:`State <module_state>` object.

The new class requires a new unique name. Add this to the `PostProcessingEnum` at the bottom of the file
with an associated title to select this distribution.

The class must have the following attributes:
    - `default_arguments`: default values for the arguments, for testing

The class must have the following methods and corresponding signatures:
    - `__init__(self, state, simulation_cell, parameters)`
    - `run(self)`

The `__init__` function should process the parameters. The `run` method should be the primary location
for the implementation and return a :ref:`State <module_state>` object.
