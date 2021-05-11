import numpy as np
from shapely.geometry import Point


def get_random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if poly.contains(p):
            return p


def normal_distribution(mean, sigma):
    """
    Returns a single number from a Gaussian distribution with the given parameters.
    """
    return np.random.normal(loc=mean, scale=sigma)