import numpy as np


def get_surface_height(simulation_cell, coordinates, percentage_of_box_to_search=80.0):
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (percentage_of_box_to_search / 100)
    z = [xyz[2] for xyz in coordinates if xyz[2] < cutoff]
    return max(z)


def wrap_periodic_coordinates_in_z(coordinates, simulation_cell):
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    return [coordinates[ii] - simulation_cell["z_vector"] if z > (lz * 0.8) else coordinates[ii]
            for ii, (x, y, z) in enumerate(coordinates)]


def periodic_images_xy(coordinates, simulation_cell, num_copies=1):
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


def generate_neighbour_list(coordinates, simulation_cell, bonding_distance_cutoff):
    neighbour_list = list()
    coordinates = wrap_periodic_coordinates_in_z(coordinates, simulation_cell)
    coordinates = np.array(coordinates)
    coordinates_periodic_xy = periodic_images_xy(coordinates, simulation_cell)
    # TODO prune periodic images outside of bonding cutoff to reduce computational time
    for reference in coordinates:
        separations = [reference - atom for atom in coordinates_periodic_xy]
        distances = [np.linalg.norm(s) for s in separations]
        neighbours = [1 for d in distances if d < bonding_distance_cutoff]
        neighbour_list.append(sum(neighbours))
    return neighbour_list


def check_min_neighbours(settings, simulation_cell, coordinates):
    if settings["deposition_type"] == "monatomic":
        min_neighbours = 1
    elif settings["deposition_type"] == "diatomic":
        min_neighbours = 2
    bonding_distance_cutoff = settings["bonding_distance_cutoff_Angstroms"]
    neighbour_list = generate_neighbour_list(coordinates, simulation_cell, bonding_distance_cutoff)
    if np.any(np.less_equal(neighbour_list, min_neighbours)):
        raise RuntimeWarning("one or more atoms has too few neighbouring atoms")


def check_bonding_at_lower_interface(settings, simulation_cell, coordinates, elements):
    deposited_element = settings["deposition_element"]
    bonding_distance_cutoff = settings["bonding_distance_cutoff_Angstroms"]
    coordinates = wrap_periodic_coordinates_in_z(coordinates, simulation_cell)
    min_z = min([xyz[2] for xyz in coordinates])
    deposited_coordinates_z = [xyz[2] for element, xyz in zip(elements, coordinates) if element == deposited_element]
    distance_from_lower_interface = np.abs(np.array(deposited_coordinates_z) - min_z)
    if np.any(np.less_equal(distance_from_lower_interface, bonding_distance_cutoff)):
        raise RuntimeWarning("one or more deposited atoms has bonded to the lower interface")
