import logging

import numpy as np
from pymatgen.core.periodic_table import Element

from src import maths, physics, structural_analysis


def generate(settings, driver, coordinates, elements, velocities):
    num_deposited = settings["num_deposited_per_iteration"]
    gas_temperature = settings["deposition_temperature"]
    deposition_type = settings["deposition_type"]
    deposition_height = settings["deposition_height_Angstroms"]
    minimum_velocity = settings["minimum_deposition_velocity_metres_per_second"]
    deposition_element = Element(settings["deposition_element"])
    particle_mass = deposition_element.atomic_mass * physics.CONSTANTS["AtomicMassUnit_kg"]
    velocity_scaling = driver.settings["velocity_scaling_from_metres_per_second"]
    surface_height = structural_analysis.get_surface_height(driver.substrate, coordinates)
    new_z_position = surface_height + deposition_height

    logging.info(f"generating coordinates and velocities for deposited atom(s)")
    for ii in range(num_deposited):
        if deposition_type == "monatomic":
            coordinates_new = random_monatomic_position(driver.substrate, new_z_position)
            elements_new = list(deposition_element.name)
            velocities_new = random_monatomic_velocity(gas_temperature, particle_mass, minimum_velocity)
        elif deposition_type == "diatomic":
            bond_length = float(settings["diatomic_bond_length_Angstroms"])
            coordinates_new = random_diatomic_position(driver.substrate, new_z_position, bond_length)
            elements_new = [deposition_element.name for _ in range(2)]
            velocities_new = random_diatomic_velocities(gas_temperature, particle_mass, bond_length, minimum_velocity)
        else:
            logging.warning("deposition_type must be either 'monatomic' or 'diatomic'")
            raise ValueError(f"deposition_type {deposition_type} is unknown")

        coordinates = np.vstack((coordinates, coordinates_new))
        elements = elements + elements_new
        velocities = np.vstack((velocities, velocities_new * velocity_scaling))

    return coordinates, elements, velocities


def random_monatomic_position(substrate, new_z_position):
    base_polygon_coordinates = [(substrate["xlo"], substrate["ylo"]),
                                (substrate["xhi"], substrate["ylo"]),
                                (substrate["xlo"] + substrate["xy"], substrate["yhi"]),
                                (substrate["xhi"] + substrate["xy"], substrate["yhi"])]
    relative_height = new_z_position / (substrate["zhi"] - substrate["zlo"])
    relative_shift = substrate["zvec"] * relative_height
    polygon_coordinates = np.add(base_polygon_coordinates, relative_shift[0:1])
    point = maths.get_random_point_in_polygon(polygon_coordinates)
    return np.array((point.x, point.y, new_z_position))


def random_monatomic_velocity(gas_temperature, particle_mass, minimum_velocity, max_iterations=10000):
    vx = physics.velocity_from_normal_distribution(gas_temperature, particle_mass)
    vy = physics.velocity_from_normal_distribution(gas_temperature, particle_mass)
    for ii in range(max_iterations):
        vz = np.abs(physics.velocity_from_normal_distribution(gas_temperature, particle_mass))
        if vz > minimum_velocity:
            return np.array((vx, vy, -vz))
    raise ValueError(f"failed to generate a velocity greater than the specified minimum of "
                     f"{minimum_velocity} m/s after {max_iterations} iterations")


def random_diatomic_position(substrate, new_z_position, bond_length):
    centre = random_monatomic_position(substrate, new_z_position)
    position1 = centre.copy()
    position2 = centre.copy()
    position1[0] += bond_length / 2
    position2[0] -= bond_length / 2
    return np.array((position1, position2))


def random_diatomic_velocities(gas_temperature, particle_mass, bond_length, minimum_velocity, max_iterations=10000):
    moment_of_inertia = (particle_mass / 2) * pow(bond_length, 2)
    rotational_xz = physics.velocity_from_normal_distribution(gas_temperature, moment_of_inertia)
    rotational_xy = physics.velocity_from_normal_distribution(gas_temperature, moment_of_inertia)
    tangential_xz = rotational_xz * (bond_length / 2)
    tangential_xy = rotational_xy * (bond_length / 2)
    vx, vy, vz = random_monatomic_velocity(gas_temperature, 2 * particle_mass, minimum_velocity, max_iterations)
    vy1 = vy + tangential_xz
    vy2 = vy - tangential_xz
    vz1 = vz + tangential_xy
    vz2 = vz - tangential_xy
    return np.array(((vx, vy1, vz1), (vx, vy2, vz2)))
