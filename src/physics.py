import math
from src import maths

CONSTANTS = {
    "BoltzmannConstant": 1.380658e-23,  # Joules per Kelvin
    "AtomicMassUnit_kg": 1.66053906660e-27  # kg
}


def get_canonical_variance(num_atoms, temperature=300.0):
    """
    Uses Equation 6 from Holian et al. DOI: 10.1103/PhysRevE.52.2338

    :param num_atoms: the number of atoms in the simulation
    :param temperature: temperature of the simulation in Kelvin
    :return canonical_variance: the expected variance for N particles
    """
    num_dimensions = 3.0
    canonical_variance = (2 * pow(temperature, 2)) / (num_dimensions * num_atoms)
    return canonical_variance


def velocity_from_normal_distribution(gas_temperature, particle_mass, mean=0):
    kb = CONSTANTS["BoltzmannConstant"]
    sigma = math.sqrt((kb * gas_temperature) / particle_mass)
    return maths.normal_distribution(mean, sigma)