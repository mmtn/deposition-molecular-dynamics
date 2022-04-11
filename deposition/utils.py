import logging

import numpy as np
from pymatgen.core import IStructure, PeriodicSite
from pymatgen.core.lattice import Lattice
from pymatgen.io.lammps.data import lattice_2_lmpbox

from deposition import input_schema
from deposition.drivers.driver_enums import DriverEnum
from deposition.enums import SettingsEnum


def get_simulation_cell(simulation_cell):
    """
    Additional geometry of the simulation cell is calculated using routines from the
    `pymatgen` module including bounds specification for use with LAMMPS and the cell
    vectors

    Arguments:
        simulation_cell (dict): simulation cell settings
            (see :meth:`format <deposition.schema_definitions.simulation_cell_schema>`)
    Return:
        simulation_cell (dict): updated simulation cell with additional geometry
    """
    simulation_cell = input_schema.simulation_cell_schema.validate(simulation_cell)
    lammps_box, _ = lattice_2_lmpbox(Lattice.from_parameters(**simulation_cell))

    if lammps_box.tilt is None:
        tilt_xy, tilt_xz, tilt_yz = (0, 0, 0)
    else:
        tilt_xy, tilt_xz, tilt_yz = lammps_box.tilt

    x_min = lammps_box.bounds[0][0]
    x_max = lammps_box.bounds[0][1]
    y_min = lammps_box.bounds[1][0]
    y_max = lammps_box.bounds[1][1]
    z_min = lammps_box.bounds[2][0]
    z_max = lammps_box.bounds[2][1]

    additional_geometry_information = {
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "z_min": z_min,
        "z_max": z_max,
        "tilt_xy": tilt_xy,
        "tilt_xz": tilt_xz,
        "tilt_yz": tilt_yz,
        "x_vector": np.array((x_max - x_min, 0, 0)),
        "y_vector": np.array((tilt_xy, y_max - y_min, 0)),
        "z_vector": np.array((tilt_xz, tilt_yz, z_max - z_min)),
        "lammps_box": lammps_box,
    }

    simulation_cell.update(additional_geometry_information)

    return simulation_cell


def get_molecular_dynamics_driver(
    driver_settings,
    simulation_cell,
    deposition_time_picoseconds,
    relaxation_time_picoseconds,
):
    """
    Initialises one of the available molecular dynamics drivers. For more information
    about drivers see :ref:`here <drivers>`.

    Arguments:
        driver_settings (dict): settings for the specified driver
        simulation_cell (dict): size and shape of the simulation cell
        deposition_time_picoseconds (int or float): how long to run the deposition stage
        relaxation_time_picoseconds (int or float): how long to run the relaxation stage

    Returns:
        driver (MolecularDynamicsDriver): driver object
    """
    driver_name = driver_settings["name"]

    try:
        driver_class = DriverEnum[driver_name].value
    except KeyError:
        raise ValueError(f"no driver with the name '{driver_name}' was found")

    # for driver in DriverEnum:
    #     if driver_name == driver.name:
    #         driver_class = driver.value
    #         break
    # else:
    #     raise ValueError(f"no driver with the name '{chosen_driver}' was found")

    simulation_cell_full = get_simulation_cell(simulation_cell)
    driver = driver_class(driver_settings, simulation_cell_full)

    input_schema.check_input_file_syntax(driver)
    driver.settings.update(
        {SettingsEnum.DEPOSITION_TIME.value: deposition_time_picoseconds}
    )
    driver.settings.update(
        {SettingsEnum.RELAXATION_TIME.value: relaxation_time_picoseconds}
    )
    logging.info(f"Using driver for {driver_name}")

    return driver


def generate_neighbour_list(simulation_cell, coordinates, bonding_distance_cutoff):
    """
    Create a neighbour list for the current state to check for isolated atoms
    or molecules.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation
        cell
        coordinates (np.array): coordinate data
        bonding_distance_cutoff (float): distance below which to consider atoms
        bonded (Angstroms)

    Returns:
        neighbour_list (list): list of integers counting the neighbours of each atom
    """
    lattice = Lattice.from_parameters(**simulation_cell)
    fake_elements = ["X" for _ in range(len(coordinates))]
    sites = [
        PeriodicSite(element, coordinate, lattice, coords_are_cartesian=True)
        for element, coordinate in zip(fake_elements, coordinates)
    ]
    structure = IStructure.from_sites(sites)
    neighbours = structure.get_all_neighbors(bonding_distance_cutoff)
    neighbour_list = [len(atom_neighbours) for atom_neighbours in neighbours]
    return neighbour_list


def wrap_coordinates_in_z(simulation_cell, coordinates, percentage_of_box=80):
    """
    Take cartesian state and wrap those at the top of the box back the main
    structure at the bottom of the box. This will set negative z_plane-state for those
    atoms which are wrapped.

    Arguments:
        simulation_cell (dict): size and shape of the simulation cell
        coordinates (np.array): coordinate data
        percentage_of_box (float): how much of the cell is not wrapped

    Returns:
        wrapped_coordinates (np.array): coordinate data where high z_plane-values are
        wrapped to negative z_plane-values
    """
    lz = simulation_cell["z_max"] - simulation_cell["z_min"]
    cutoff = lz * (percentage_of_box / 100)
    return [
        coordinates[ii] - simulation_cell["z_vector"] if z > cutoff else coordinates[ii]
        for ii, (x, y, z) in enumerate(coordinates)
    ]
