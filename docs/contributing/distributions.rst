.. _contributing_distributions:

Adding position and velocity distributions
==========================================

New distributions should be written as Python classes in `deposition/distributions.py` following the example
of the preexisting classes. All position and velocity distributions should return a tuple of three float values.


Position distributions
----------------------

Position distributions define the algorithm by which newly added atoms and molecules are located in the simulation
cell.

Each new class requires a new unique name. Add this to the `PositionDistributionEnum` at the bottom of the file along
with an associated title to select this distribution.

The class must have the following attributes:
    - `num_arguments`: the number of arguments required for the distribution
    - `default_arguments`: default values for the arguments, for testing

The class must have the following methods and corresponding signatures:
    - `__init__(self, polygon_coordinates, z, arguments)`
    - `get_position(self)`

The `__init__` function should process the arguments. The `get_position` method should be the primary location
for the implementation and return a tuple of three float values.


Velocity distributions
----------------------

Velocity distributions define the algorithm by which the velocity of newly added atoms and molecules is determined.

Each new class requires a new unique name. Add this to the `VelocityDistributionEnum` at the bottom of the file along
with an associated title to select this distribution.

The class must have the following attributes:
    - `num_arguments`: the number of arguments required for the distribution
    - `default_arguments`: default values for the arguments, mostly for testing

The class must have the following methods and corresponding signatures:
    - `__init__(self, arguments)`
    - `get_velocity(self)`

The `__init__` function should process the arguments. The `get_velocity` method should be the primary location
for the implementation and return a tuple of three float values.
