import logging

import numpy as np
from pymatgen.core.periodic_table import Element

from deposition import maths, physics, structural_analysis


def append_new_coordinates_and_velocities(settings, coordinates, elements, velocities, simulation_cell,
                                          velocity_scaling):
    """
    Randomly generate new atoms based on the deposition settings and add them to the existing structure.

    Arguments:
        settings (dict): settings of the deposition calculation
        coordinates (np.array): coordinate data
        elements (list of str): atomic species data
        velocities (np.array): velocity data
        simulation_cell (dict): specification of the size and shape of the simulation cell
        velocity_scaling (float): value to rescale velocities from SI units to the units used by the MD software

    Returns:
        coordinates, elements, velocities (tuple)
            - coordinates (np.array): coordinate data
            - elements (list of str): atomic species data
            - velocities (np.array): velocity data
    """
    num_deposited = settings["num_deposited_per_iteration"]
    gas_temperature = settings["deposition_temperature_Kelvin"]
    deposition_type = settings["deposition_type"]
    minimum_velocity = settings["minimum_deposition_velocity_metres_per_second"]
    surface_height = structural_analysis.get_surface_height(simulation_cell, coordinates)
    new_z_position = surface_height + settings["deposition_height_Angstroms"]

    logging.info(f"generating coordinates and velocities for deposited atom(s)")
    for ii in range(num_deposited):
        if deposition_type == "monatomic":
            deposition_element = Element(settings["deposition_element"])
            particle_mass = deposition_element.atomic_mass * physics.CONSTANTS["AtomicMassUnit_kg"]
            coordinates_new = random_position(simulation_cell, new_z_position)
            elements_new = [deposition_element.name for _ in range(1)]
            velocities_new = random_velocity(gas_temperature, particle_mass, minimum_velocity)
        elif deposition_type == "diatomic":
            deposition_element = Element(settings["deposition_element"])
            particle_mass = deposition_element.atomic_mass * physics.CONSTANTS["AtomicMassUnit_kg"]
            bond_length = float(settings["diatomic_bond_length_Angstroms"])
            coordinates_new = random_diatomic_position(simulation_cell, new_z_position, bond_length)
            elements_new = [deposition_element.name for _ in range(2)]
            velocities_new = random_diatomic_velocities(gas_temperature, particle_mass, bond_length, minimum_velocity)
        else:
            logging.warning("deposition_type must be either 'monatomic' or 'diatomic'")
            raise ValueError(f"deposition_type {deposition_type} is unknown")

        coordinates = np.vstack((coordinates, coordinates_new))
        elements = elements + elements_new
        velocities = np.vstack((velocities, velocities_new * velocity_scaling))

    return coordinates, elements, velocities


def random_position(simulation_cell, new_z_position):
    """
    Randomly generate a position within the simulation cell on a plane at the specified z-coordinate.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        new_z_position (float): height in z of the newly added particle(s) (Angstroms)

    Returns:
        new_position (np.array): coordinates of the newly added particle(s)
    """
    base_polygon_coordinates = [(simulation_cell["x_min"], simulation_cell["y_min"]),
                                (simulation_cell["x_max"], simulation_cell["y_min"]),
                                (simulation_cell["x_min"] + simulation_cell["tilt_xy"], simulation_cell["y_max"]),
                                (simulation_cell["x_max"] + simulation_cell["tilt_xy"], simulation_cell["y_max"])]
    relative_height = new_z_position / (simulation_cell["z_max"] - simulation_cell["z_min"])
    relative_shift = simulation_cell["z_vector"] * relative_height
    polygon_coordinates = np.add(base_polygon_coordinates, relative_shift[0:1])
    new_x_position, new_y_position = maths.get_random_point_in_polygon(polygon_coordinates)
    return np.array((new_x_position, new_y_position, new_z_position))


def random_velocity(gas_temperature, particle_mass, minimum_velocity, max_iterations=10000):
    """
    Randomly generate the velocity of the newly added particles(s) based on the kinetic temperature and mass.

    Arguments:
        gas_temperature (float): temperature of the deposition material (Kelvin)
        particle_mass (float): mass of the particle(s) to be added (kg)
        minimum_velocity (float): sets a minimum bound on the generated velocity (m/s)
        max_iterations (int): sets an upper bound when trying to get a velocity under `minimum_velocity`

    Returns:
        new_velocity (np.array): velocity of the newly added particle(s)
    """
    vx = physics.velocity_from_normal_distribution(gas_temperature, particle_mass)
    vy = physics.velocity_from_normal_distribution(gas_temperature, particle_mass)
    for ii in range(max_iterations):
        vz = np.abs(physics.velocity_from_normal_distribution(gas_temperature, particle_mass))
        if vz > minimum_velocity:
            return np.array((vx, vy, -vz))
    raise ValueError(f"failed to generate a velocity greater than the specified minimum of {minimum_velocity} m/s "
                     f"after {max_iterations} iterations")


def random_diatomic_position(simulation_cell, new_z_position, bond_length):
    """
    Randomly generates the positions of two atoms separated by the given bond length.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        new_z_position (float): height in z of the newly added particle(s) (Angstroms)
        bond_length (float): distance between the two atoms in the diatom (Angstroms)

    Returns:
        atomic_positions (np.array): coordinates of the two bonded atoms
    """
    centre_position = random_position(simulation_cell, new_z_position)
    position_atom_1 = centre_position.copy()
    position_atom_2 = centre_position.copy()
    position_atom_1[0] += bond_length / 2
    position_atom_2[0] -= bond_length / 2
    return np.array((position_atom_1, position_atom_2))


def random_diatomic_velocities(gas_temperature, particle_mass, bond_length, minimum_velocity, max_iterations=10000):
    """
    Randomly generates the velocities of two atoms separated by the given bond length.

    Arguments:
        gas_temperature (float): temperature of the deposition material (Kelvin)
        particle_mass (float): mass of the particle(s) to be added (kg)
        bond_length (float): distance between the two atoms in the diatom (Angstroms)
        minimum_velocity (float): sets a minimum bound on the generated velocity (m/s)
        max_iterations (int): sets an upper bound when trying to get a velocity under `minimum_velocity`

    Returns:
        atomic_velocities (np.array): velocities of the two bonded atoms
    """
    moment_of_inertia = (particle_mass / 2) * pow(bond_length, 2)
    rotational_xz = physics.velocity_from_normal_distribution(gas_temperature, moment_of_inertia)
    rotational_xy = physics.velocity_from_normal_distribution(gas_temperature, moment_of_inertia)
    tangential_xz = rotational_xz * (bond_length / 2)
    tangential_xy = rotational_xy * (bond_length / 2)
    vx, vy, vz = random_velocity(gas_temperature, 2 * particle_mass, minimum_velocity, max_iterations)
    vy1 = vy + tangential_xz
    vy2 = vy - tangential_xz
    vz1 = vz + tangential_xy
    vz2 = vz - tangential_xy
    return np.array(((vx, vy1, vz1), (vx, vy2, vz2)))
