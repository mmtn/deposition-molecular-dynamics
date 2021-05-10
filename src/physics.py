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
