import numpy as np


def normal_distribution(mean, sigma):
    """
    Returns a single number from a Gaussian distribution with the given parameters.
    """
    return np.random.normal(loc=mean, scale=sigma)