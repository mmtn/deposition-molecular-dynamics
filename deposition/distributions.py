import math
from enum import Enum

import numpy as np
from deposition import physics
from matplotlib import path as mplpath


def get_position_distribution(name, polygon_coordinates, z_plane, arguments=None):
    """
    Returns a position distribution object

    Arguments:
        name (str): string used to choose a particular distribution
        arguments (list): arguments to pass to constructor
        polygon_coordinates (np.array): xy-state of the polygon within which to generate a position
        z_plane (float): z-coordinate of the position

    Returns:
        Position distribution object
    """
    try:
        position_class = PositionDistributionEnum[name].value
        return position_class(polygon_coordinates, z_plane, arguments)
    except KeyError:
        raise ValueError(f"unknown position distribution: {name}")


def get_velocity_distribution(name, arguments=None):
    """
    Returns a velocity distribution object

    Arguments:
        name (str): string used to choose a particular distribution
        arguments (list): arguments to pass to constructor

    Returns:
        Velocity distribution object
    """
    try:
        velocity_class = VelocityDistributionEnum[name].value
        return velocity_class(arguments)
    except KeyError:
        raise ValueError(f"unknown velocity distribution: {name}")


"""Position distribution classes"""


class FixedPositionDistribution:
    """Returns the specified position"""

    num_arguments = 2
    default_arguments = (0.0, 0.0)

    def __init__(self, polygon_coordinates, z, arguments):
        if arguments is None:
            arguments = self.default_arguments
        assert (
            len(arguments) == self.num_arguments
        ), f"{self.__class__} requires {self.num_arguments} argument(s)"
        self.polygon_coordinates = polygon_coordinates
        self.z = z
        self.x = float(arguments[0])
        self.y = float(arguments[1])

    def get_position(self):
        return self.x, self.y, self.z


class UniformPositionDistribution:
    """Returns a uniformly random position within the polygon"""

    num_arguments = 0
    _max_iterations = 10000

    def __init__(self, polygon_coordinates, z, arguments=None):
        self.polygon_coordinates = polygon_coordinates
        self.z = z

    def get_position(self):
        polygon = mplpath.Path(self.polygon_coordinates)
        bbox = polygon.get_extents()
        for iteration in range(self._max_iterations):
            point = (
                np.random.uniform(bbox.xmin, bbox.xmax),
                np.random.uniform(bbox.ymin, bbox.ymax),
            )
            if polygon.contains_point(point):
                return point[0], point[1], self.z
        raise RuntimeError("generation of random position failed")


"""Velocity distribution classes"""


class FixedVelocityDistribution:
    """Returns the specified velocity"""

    num_arguments = 3
    default_arguments = (0.0, 0.0, -100.0)

    def __init__(self, arguments):
        if arguments is None:
            arguments = self.default_arguments
        assert (
            len(arguments) == self.num_arguments
        ), f"{self.__class__} requires {self.num_arguments} argument(s)"
        self.vx = float(arguments[0])
        self.vy = float(arguments[1])
        self.vz = float(arguments[2])

    def get_velocity(self):
        return self.vx, self.vy, self.vz


class GaussianVelocityDistribution:
    """
    Returns a velocity in metres per second randomly selected from a normal distribution.
    Uses the gas_temperature (Kelvin), particle_mass (kg), and mean value (m/s).
    """

    num_arguments = 3
    default_arguments = (300.0, 1e-25, 0.0)

    def __init__(self, arguments):
        if arguments is None:
            arguments = self.default_arguments
        assert (
            len(arguments) == self.num_arguments
        ), f"{self.__class__} requires {self.num_arguments} argument(s)"
        self.gas_temperature = float(arguments[0])
        self.particle_mass = float(arguments[1])
        self.mean = arguments = float(arguments[2])

    def get_single_velocity(self):
        sigma = math.sqrt(
            (physics.CONSTANTS["BoltzmannConstant"] * self.gas_temperature)
            / self.particle_mass
        )
        return np.random.normal(loc=self.mean, scale=sigma)

    def get_velocity(self):
        vx = self.get_single_velocity()
        vy = self.get_single_velocity()
        vz = self.get_single_velocity()
        return vx, vy, vz


"""Distribution Enums"""


class PositionDistributionEnum(Enum):
    fixed = FixedPositionDistribution
    uniform = UniformPositionDistribution


class VelocityDistributionEnum(Enum):
    fixed = FixedVelocityDistribution
    gaussian = GaussianVelocityDistribution
