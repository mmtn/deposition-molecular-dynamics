import numpy as np
from pymatgen.core.lattice import Lattice
from pymatgen.core.sites import PeriodicSite
from pymatgen.core.structure import IMolecule, IStructure


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


def generate_neighbour_list(simulation_cell, coordinates, bonding_distance_cutoff):
    """
    Create a neighbour list for the current coordinates to check for isolated atoms or molecules.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        bonding_distance_cutoff (float): distance below which to consider atoms bonded (Angstroms)

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


def check_minimum_neighbours(simulation_cell, coordinates, num_deposited_atoms, bonding_distance_cutoff):
    """
    Assess the number of neighbours of all simulated atoms to check that everything is bonded together and there are not
    multiple isolated regions.

    Arguments:
        simulation_cell (dict): specification of the size and shape of the simulation cell
        coordinates (np.array): coordinate data
        num_deposited_atoms (int): how many atoms are deposited in each iteration
        bonding_distance_cutoff (float): distance below which to consider atoms bonded (Angstroms)
    """
    neighbour_list = generate_neighbour_list(simulation_cell, coordinates, bonding_distance_cutoff)
    if np.any(np.less_equal(neighbour_list, num_deposited_atoms)):
        raise RuntimeWarning("one or more atoms has too few neighbouring atoms")
