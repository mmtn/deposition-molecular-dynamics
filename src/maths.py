import numpy as np
from shapely.geometry import Polygon, Point


def get_random_point_in_polygon(polygon_coordinates):
    """

    :param polygon_coordinates:
    :return point:
    """
    polygon = Polygon(polygon_coordinates)
    x_min, y_min, x_max, y_max = polygon.bounds
    while True:
        point = Point(np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max))
        if polygon.contains(point):
            return point


def normal_distribution(mean, sigma):
    """
    Returns a single number from a Gaussian distribution with the given parameters.
    """
    return np.random.normal(loc=mean, scale=sigma)
