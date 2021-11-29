import math

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
    sigma = math.sqrt((CONSTANTS["BoltzmannConstant"] * gas_temperature) / particle_mass)
    return maths.normal_distribution(mean, sigma)
