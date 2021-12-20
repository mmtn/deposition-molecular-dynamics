import numpy as np


def get_surface_height(simulation_cell, coordinates, percentage_of_box=80):
    """
    Crude method to find the surface of the existing structure by finding the maximum
    z-coordinate in the lower 80% of the simulation cell (by default).

    Arguments:
        simulation_cell (dict): size and shape of the simulation cell
        coordinates (np.array): coordinate data
        percentage_of_box (float): how much of the cell to look in for a surface

    Returns:
        surface_height (float): the surface height of the existing structure (Angstroms)
    """
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (percentage_of_box / 100)
    z = [xyz[2] for xyz in coordinates if xyz[2] < cutoff]
    return max(z)


def wrap_coordinates_in_z(simulation_cell, coordinates, percentage_of_box=80):
    """
    Take cartesian coordinates and wrap those at the top of the box back the main
    structure at the bottom of the box. This will set negative z-coordinates for those
    atoms which are wrapped.

    Arguments:
        simulation_cell (dict): size and shape of the simulation cell
        coordinates (np.array): coordinate data
        percentage_of_box (float): how much of the cell is not wrapped

    Returns:
        wrapped_coordinates (np.array): coordinate data where high z-values are
        wrapped to negative z-values
    """
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (percentage_of_box / 100)
    return [
        coordinates[ii] - simulation_cell["z_vector"] if z > cutoff else coordinates[ii]
        for ii, (x, y, z) in enumerate(coordinates)
    ]
