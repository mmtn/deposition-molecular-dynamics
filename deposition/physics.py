import logging
import math

import numpy as np
from pymatgen.core import Element

from deposition import maths

CONSTANTS = {
    "BoltzmannConstant": 1.380658e-23,  # Joules per Kelvin
    "AtomicMassUnit_kg": 1.66053906660e-27  # kg
}
"""
Define physical constants of the universe used by other functions.
"""


def get_canonical_variance(num_atoms, temperature=300.0):
    """
    The dependence of the temperature variance in the Nose-Hoover thermostat on the number of atoms and the temperature
    of the system has been studied by `Holian et al.`_ This function implements Equation 6 from this paper

    .. math::

       \\sigma^2(d, T, N) = \\frac{2}{d} \\frac{T^2}{N}

    where :math:`\\sigma^2` is the variance, `d` is the number of dimensions, `T` is the temperature, and `N` is the
    number of atoms.

    Arguments:
        num_atoms (int): the number of atoms in the simulation
        temperature (float, default=300.0): temperature of the simulation in Kelvin

    Returns:
        canonical_variance (float): the expected variance for N particles at the given temperature

    .. _Holian et al.: https://www.doi.org/10.1103/PhysRevE.52.2338
    """
    num_dimensions = 3.0
    canonical_variance = (2 * pow(temperature, 2)) / (num_dimensions * num_atoms)
    return canonical_variance


def velocity_from_normal_distribution(gas_temperature, particle_mass, mean=0.0):
    """
    Return a velocity in metres per second randomly selected from a normal distribution.

    Arguments:
        gas_temperature (float): temperature of the ideal gas in Kelvin
        particle_mass (float): mass of the particle in kg
        mean (float): centre of the distribution in metres per second

    Returns:
        random velocity in metres per second (float)
    """
    if particle_mass > 0:
        sigma = math.sqrt((CONSTANTS["BoltzmannConstant"] * gas_temperature) / particle_mass)
        return maths.normal_distribution(mean, sigma)
    else:
        logging.warning("Particle mass in velocity calculation is zero, returning zero velocity. Note: this could be "
                        "due to a calculated zero for moment of inertia if you are depositing an on-axis molecule")
        return 0


def get_centre_of_mass(coordinates, elements):
    """
    Calculates the centre of mass

    Arguments:
        coordinates (array): coordinates of the atoms
        elements (list): list of str with element names

    Returns:
        centre_of_mass, masses (tuple)
            - centre_of_mass (array): xyz coordinate of the centre of mass
            - masses (list): list of the atomic masses in kg
    """
    atoms = [Element(e) for e in elements]
    masses = [CONSTANTS["AtomicMassUnit_kg"] * float(atom.atomic_mass) for atom in atoms]
    centre_of_mass_list = [mass * coordinate for mass, coordinate in zip(masses, coordinates)]
    centre_of_mass = np.sum(centre_of_mass_list, axis=0) / np.sum(masses)
    return centre_of_mass, masses


def get_moment_of_inertia(coordinates, elements):
    """
    Calculates the moment of inertia

    Arguments:
        coordinates (array): coordinates of the atoms
        elements (list): list of str with element names

    Returns:
        moment_of_inertia (array): moment of inertia around the x, y, and z axes

    """
    centre_of_mass, masses = get_centre_of_mass(coordinates, elements)
    distances = [np.subtract(coordinate, centre_of_mass) for coordinate in coordinates]
    mass_distance_product = np.atleast_2d([mass * np.abs(distance) for mass, distance in zip(masses, distances)])
    moment_of_inertia = np.sum(mass_distance_product, axis=0)
    return moment_of_inertia


