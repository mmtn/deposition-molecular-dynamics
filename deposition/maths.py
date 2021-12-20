import numpy as np
from matplotlib import path as mplpath


def get_random_point_in_polygon(polygon_coordinates):
    """
    Use the `shapely` package to find a random point within the specified polygon.

    Arguments:
        polygon_coordinates (np.array): coordinates defining the shape of the polygon

    Returns:
        point (tuple):
            - x (float): x-coordinate of the randomly generated point
            - y (float): y-coordinate of the randomly generated point
    """
    polygon = mplpath.Path(polygon_coordinates)
    bbox = polygon.get_extents()
    while True:
        point = (
            np.random.uniform(bbox.xmin, bbox.xmax),
            np.random.uniform(bbox.ymin, bbox.ymax),
        )
        if polygon.contains_point(point):
            return point[0], point[1]


def normal_distribution(mean, sigma):
    """
    Uses the `numpy.random.normal` function to generate random values from a normal distribution.

    Arguments:
        mean (float): the centre of the normal distribution
        sigma (float): the standard deviation of the normal distribution

    Returns:
        randomly distributed value (float)
    """
    return np.random.normal(loc=mean, scale=sigma)
