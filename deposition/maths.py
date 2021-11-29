import numpy as np
from shapely.geometry import Point, Polygon


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
    polygon = Polygon(polygon_coordinates)
    x_min, y_min, x_max, y_max = polygon.bounds
    while True:
        point = Point(np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max))
        if polygon.contains(point):
            return point.x, point.y


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
