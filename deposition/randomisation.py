import logging

import numpy as np

from deposition import distributions, io, physics
from deposition.input_schema import DepositionTypeEnum


def new_coordinates_and_velocities(settings, state, simulation_cell, velocity_scaling):
    """
    Randomly generate new atoms based on the deposition settings and add them to the
    existing structure.

    Arguments:
        settings: settings of the deposition calculation
        state: coordinates, elements, velocities
        simulation_cell (dict): size and shape of the simulation cell
        velocity_scaling (float): value to rescale velocities from SI units to the units used by the MD software

    Returns:
        state: coordinates, elements, velocities
    """

    def get_surface_height(simulation_cell, coordinates, percentage_of_box=80):
        """
        Crude method to find the surface of the existing structure by finding the maximum
        z_plane-coordinate in the lower 80% of the simulation cell (by default).
        """
        box_height = simulation_cell["z_max"] - simulation_cell["z_min"]
        cutoff = box_height * (percentage_of_box / 100)
        z = [xyz[2] for xyz in coordinates if xyz[2] < cutoff]
        return max(z)

    surface_height = get_surface_height(simulation_cell, state.coordinates)
    new_z_position = surface_height + settings.deposition_height
    polygon_coordinates = get_polygon_on_plane(simulation_cell, new_z_position)
    position_distribution = distributions.get_position_distribution(
        settings.position_distribution,
        polygon_coordinates,
        new_z_position,
        settings.position_distribution_parameters,
    )
    velocity_distribution = distributions.get_velocity_distribution(
        settings.velocity_distribution,
        settings.velocity_distribution_parameters,
    )

    logging.info(f"generating coordinates and velocities for deposited atom(s)")
    for ii in range(settings.num_deposited_per_iteration):
        if settings.deposition_type == DepositionTypeEnum.MONATOMIC.name:
            deposition_coordinates = [0, 0, 0]
            deposition_elements = [settings.deposition_element]
        elif settings.deposition_type == DepositionTypeEnum.MOLECULE.name:
            molecule = io.read_xyz(settings.molecule_xyz_file)
            deposition_coordinates = molecule.coordinates
            deposition_elements = molecule.elements
        else:
            raise ValueError(f"unknown deposition type: {settings.deposition_type}")

        new_coordinates = get_new_positions(
            position_distribution, deposition_coordinates
        )
        new_elements = deposition_elements
        new_velocities = get_new_velocities(
            velocity_distribution,
            deposition_coordinates,
            deposition_elements,
            settings.deposition_temperature,
            settings.min_velocity,
        )

        state.coordinates = np.vstack((state.coordinates, new_coordinates))
        state.elements = state.elements + new_elements
        state.velocities = np.vstack(
            (state.velocities, new_velocities * velocity_scaling)
        )

    return state


def get_polygon_on_plane(simulation_cell, z_plane):
    """
    Get the state at the boundaries of the simulation cell at a particular z_plane
    plane.

    Arguments:
        simulation_cell (dict): the size and shape of the simulation cell
        z_plane (float): at which height to calculate the polygon state (
        Angstroms)

    Returns:
        polygon_coordinates (np.array): state describing the plane
    """
    # Note: order matters in this list. These points draw a matplotlib path.
    base_polygon_coordinates = [
        (simulation_cell["x_min"], simulation_cell["y_min"]),
        (simulation_cell["x_max"], simulation_cell["y_min"]),
        (
            simulation_cell["x_max"] + simulation_cell["tilt_xy"],
            simulation_cell["y_max"],
        ),
        (
            simulation_cell["x_min"] + simulation_cell["tilt_xy"],
            simulation_cell["y_max"],
        ),
    ]
    relative_height = z_plane / (simulation_cell["z_max"] - simulation_cell["z_min"])
    relative_shift = simulation_cell["z_vector"] * relative_height
    polygon_coordinates = np.add(base_polygon_coordinates, relative_shift[0:1])
    return polygon_coordinates


def random_velocity(velocity_distribution, minimum_velocity, max_iterations=10000):
    """
    Randomly generate the velocity of the newly added particles(s) based on the
    kinetic temperature and mass.

    Arguments:
        velocity_distribution: functional form for obtaining the new velocity
        minimum_velocity (float): minimum bound on the generated velocity (m/s)
        max_iterations (int): upper bound when trying to get a velocity under
        `min_velocity`

    Returns:
        new_velocity (np.array): velocity of the newly added particle(s)
    """
    for ii in range(max_iterations):
        vx, vy, vz = velocity_distribution.get_velocity()
        vz = np.abs(vz)
        if vz > minimum_velocity:
            return np.array((vx, vy, -vz))
    raise ValueError(
        f"failed to generate a velocity greater than the specified minimum of "
        f"{minimum_velocity} m/s after {max_iterations} iterations"
    )


def get_new_positions(position_distribution, molecule_coordinates):
    """
    Randomly generates a position within the simulation cell on a plane at the
    specified z_plane-coordinate and centres the
    atom/molecule at this point.

    Arguments:
        position_distribution: functional form for obtaining the new position
        molecule_coordinates (np.array): state of the atoms in the molecule to
        be added

    Returns:
        new_coordinates (np.array): state of the molecule placed at a randomly
        generated position in the cell
    """
    centre = molecule_coordinates - np.mean(molecule_coordinates, axis=0)
    new_coordinates = position_distribution.get_position() + centre
    return new_coordinates


def get_new_velocities(
    velocity_distribution, coordinates, elements, temperature, minimum_velocity
):
    """
    Randomly generate the velocity of the newly added molecule based on the kinetic
    temperature and mass. All atoms in the molecule are given identical velocities.

    Arguments:
        velocity_distribution: functional form for obtaining the new velocity
        coordinates (np.array): coordinate data
        elements (list of str): atomic species data
        temperature (float): deposition temperature in Kelvin
        minimum_velocity (float): minimum bound on the generated velocity (m/s)

    Returns:
        velocities (np.array): velocities of the atoms in the deposited atom/molecule
    """
    translational_velocity = random_velocity(velocity_distribution, minimum_velocity)
    translational_velocities = np.repeat(
        np.atleast_2d(translational_velocity), repeats=len(elements), axis=0
    )
    if len(elements) == 1:  # or add_rotation == False:
        return translational_velocities

    # add rotational velocities to molecules
    centre_of_mass, masses = physics.get_centre_of_mass(coordinates, elements)
    moment_of_inertia_xyz = physics.get_moment_of_inertia(coordinates, elements)
    distances = [np.subtract(coordinate, centre_of_mass) for coordinate in coordinates]
    rotational_velocities = [
        physics.velocity_from_normal_distribution(temperature, moment_of_inertia)
        if moment_of_inertia > 0
        else 0
        for moment_of_inertia in moment_of_inertia_xyz
    ]
    tangential_velocities = [rotational_velocities * distance for distance in distances]
    velocities = [
        translational + tangential
        for translational, tangential in zip(
            translational_velocities, tangential_velocities
        )
    ]
    return velocities
