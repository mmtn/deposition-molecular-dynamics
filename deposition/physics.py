import math
from deposition import maths

CONSTANTS = {
    "BoltzmannConstant": 1.380658e-23,  # Joules per Kelvin
    "AtomicMassUnit_kg": 1.66053906660e-27  # kg
}


def get_canonical_variance(num_atoms: int, temperature: float = 300.0) -> float:
    """
    The dependence of the temperature variance in the Nose-Hoover thermostat on the number of atoms and the temperature
    of the system has been studied by `Holian et al.`_ This function implements Equation 6
    from this paper.

    .. _Holian et al.: https://www.doi.org/10.1103/PhysRevE.52.2338

    :param num_atoms: the number of atoms in the simulation
    :param temperature: temperature of the simulation in Kelvin
    :return: canonical_variance: the expected variance for N particles
    """
    num_dimensions = 3.0
    canonical_variance = (2 * pow(temperature, 2)) / (num_dimensions * num_atoms)
    return canonical_variance


def velocity_from_normal_distribution(gas_temperature: float, particle_mass: float, mean: float = 0) -> float:
    """
    Return a velocity in metres per second randomly selected from a normal distribution.

    :param gas_temperature: temperature of the ideal gas in Kelvin
    :param particle_mass: mass of the particle in kg
    :param mean: centre of the distribution in metres per second
    :return: random velocity in metres per second
    """
    sigma = math.sqrt((CONSTANTS["BoltzmannConstant"] * gas_temperature) / particle_mass)
    return maths.normal_distribution(mean, sigma)
