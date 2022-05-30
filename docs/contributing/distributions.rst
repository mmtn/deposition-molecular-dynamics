.. _contributing_distributions:

Adding position and velocity distributions
==========================================

For each iteration, there must be a method of choosing the positions and velocities of any newly added particles. There
are existing implementations for a few common use cases in `deposition/distributions.py`. New distributions should be
added to this file as Python classes following the example of the preexisting classes. All position and velocity
distributions should return a tuple of three float values.


Position distributions
----------------------

Position distributions define the algorithm by which newly added atoms or molecules are located in the simulation
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

Velocity distributions define the algorithm by which the velocity of newly added atoms or molecules is determined.

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
