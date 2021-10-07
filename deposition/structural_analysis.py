import numpy as np


def get_surface_height(simulation_cell, coordinates, percentage_of_box_to_search=80.0):
    """
    Crude method to find the surface of the existing structure by finding the maximum z-coordinate in the lower 80% of
    the simulation cell (by default).

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        percentage_of_box_to_search (float): how much of the simulation cell should be considered for finding a surface

    Returns:
        surface_height (float): the surface height of the existing structure (Angstroms)
    """
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (percentage_of_box_to_search / 100)
    z = [xyz[2] for xyz in coordinates if xyz[2] < cutoff]
    return max(z)


def wrap_periodic_coordinates_in_z(simulation_cell, coordinates, cutoff_percentage=80.0):
    """
    Takes atomic coordinates in the top region of the simulation cell and shifts them to their periodic image in the
    cell below. This is useful when generating the neighbour list to assess bonding.

    NOTE: THIS IS NOT AS SIMPLE FOR NON ORTHOGONAL CELLS

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        cutoff_percentage (float): percentage of box to ignore for periodic wrapping

    Returns:
        wrapped_coordinates (np.array): coordinate data after periodic wrapping in the z-direction
    """
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (cutoff_percentage / 100)
    return [coordinates[ii] - simulation_cell["z_vector"]
            if z > cutoff else coordinates[ii]
            for ii, (x, y, z) in enumerate(coordinates)]


def generate_periodic_images_xy(simulation_cell, coordinates, num_copies=1):
    """
    Creates copies of the simulation cell in order to generate neighbour lists for periodic boundary conditions.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        num_copies:

    Returns:

    """
    coordinates_periodic_xy = coordinates
    x_shift = simulation_cell["x_vector"]
    y_shift = simulation_cell["y_vector"]
    total_copies = (num_copies * 2) + 1
    for ix, iy in np.ndindex(total_copies, total_copies):
        x = ix - num_copies
        y = iy - num_copies
        if x != 0 or y != 0:
            shift = np.add(x * x_shift, y * y_shift)
            coordinates_periodic_xy = np.append(coordinates_periodic_xy, np.add(coordinates, shift), axis=0)
    return coordinates_periodic_xy


def generate_neighbour_list(simulation_cell, coordinates, bonding_distance_cutoff):
    """
    Create a neighbour list for the current coordinates to check for isolated individual atoms or pairs of atoms.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        bonding_distance_cutoff (float): distance below which to consider atoms bonded (Angstroms)

    Returns:

    """

    # TODO: try and replace this implementation with pymatgen functionality
    # https://pymatgen.org/pymatgen.core.structure.html#pymatgen.core.structure.IStructure.get_all_neighbors
    neighbour_list = list()
    coordinates = wrap_periodic_coordinates_in_z(simulation_cell, coordinates)
    coordinates = np.array(coordinates)
    coordinates_periodic_xy = generate_periodic_images_xy(simulation_cell, coordinates)
    # TODO prune periodic images outside of bonding cutoff to reduce computational time
    for reference in coordinates:
        separations = [reference - atom for atom in coordinates_periodic_xy]
        distances = [np.linalg.norm(s) for s in separations]
        neighbours = [1 for d in distances if d < bonding_distance_cutoff]
        neighbour_list.append(sum(neighbours))
    return neighbour_list


def check_min_neighbours(simulation_cell, coordinates, deposition_type, bonding_distance_cutoff):
    """
    Assess the number of neighbours of all simulated atoms to check that everything is bonded together and there are not
    multiple isolated regions.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        deposition_type (str): style of deposition
        bonding_distance_cutoff (float): distance below which to consider atoms bonded (Angstroms)
    """
    # TODO: add global setting to raise Error rather than Warning for structural checks
    if deposition_type == "monatomic":
        min_neighbours = 1
    elif deposition_type == "diatomic":
        min_neighbours = 2
    elif deposition_type == "molecule":
        min_neighbours = 0
    else:
        raise ValueError("deposition type not recognised")
    neighbour_list = generate_neighbour_list(simulation_cell, coordinates, bonding_distance_cutoff)
    if np.any(np.less_equal(neighbour_list, min_neighbours)):
        raise RuntimeWarning("one or more atoms has too few neighbouring atoms")


def check_bonding_at_image(simulation_cell, coordinates, elements, deposited_element, bonding_distance_cutoff):
    """
    Check whether deposited atom(s) have reflected and bonded to the periodic image of the substrate.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        elements (list of str): atomic species data
        deposited_element (str): label for deposited element
        bonding_distance_cutoff (float): distance below which to consider atoms bonded (Angstroms)
    """

    # TODO: fix logic here
    # It doesn't make sense when depositing oxygen on a substrate which already contains oxygen
    coordinates = wrap_periodic_coordinates_in_z(simulation_cell, coordinates)
    deposited_coordinates_z = [xyz[2] for element, xyz in zip(elements, coordinates) if element == deposited_element]
    min_z = min([xyz[2] for xyz in coordinates])
    distance_from_lower_interface = np.abs(np.array(deposited_coordinates_z) - min_z)
    if np.any(np.less_equal(distance_from_lower_interface, bonding_distance_cutoff)):
        raise RuntimeWarning("one or more deposited atoms has bonded to the lower interface")
