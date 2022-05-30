from enum import Enum

import numpy as np

from deposition.state import State
from deposition.utils import (generate_neighbour_list, get_simulation_cell,
                              wrap_coordinates_in_z)


def run(name, state, simulation_cell, parameters=None, dry_run=False):
    """
    Runs the postprocessing check on the provided structural data.

    Args:
        name: the string referring to the check
        state: coordinates, elements, velocities
        simulation_cell: size and shape of the simulation cell
        parameters: any arguments required for the check
        dry_run: optionally skip the actual check (for validation at initialisation)
    """
    try:
        postprocessing_class = PostProcessingEnum[name].value
        routine = postprocessing_class(state, simulation_cell, parameters)
    except KeyError:
        raise ValueError(f"unknown post processing routine {name}")

    if not dry_run:
        return routine.run()


class NumNeighboursCheck:
    """
    Assess the number of neighbours of all simulated atoms to check that everything is
    bonded together and there are no isolated regions.

    Parameters:
        - min_neighbours (`int`)
            - the minimum number of neighbouring atoms for each atom
        - bonding distance cutoff (Angstroms, `int` or `float`)
            - minimum separation for two atoms to be considered bonded
    """

    num_parameters = 2
    default_parameters = (1, 4.0)

    def __init__(self, state, simulation_cell, parameters):
        if parameters is None:
            parameters = self.default_parameters
        assert (
            len(parameters) == self.num_parameters
        ), f"{self.__class__} requires {self.num_parameters} argument(s)"
        self.min_neighbours = float(parameters[0])
        self.bonding_cutoff = float(parameters[1])
        self.state = state
        self.simulation_cell = simulation_cell

    def run(self):
        neighbour_list = generate_neighbour_list(
            self.simulation_cell, self.state.coordinates, self.bonding_cutoff
        )
        if np.any(np.less_equal(neighbour_list, self.min_neighbours)):
            raise RuntimeWarning("one or more atoms has too few neighbouring atoms")
        return self.state


class ShiftToOrigin:
    """
    Relocates the entire atomic structure to the origin (0, 0, 0) at the end of each iteration
    """

    default_parameters = True

    def __init__(self, state, simulation_cell, parameters):
        if parameters is None:
            parameters = self.default_parameters
        assert type(parameters) is bool, "shift to origin routine must be True or False"
        self.state = state
        self.simulation_cell = simulation_cell

    def run(self):
        """Moves the given state back to the origin at (0, 0, 0)"""
        full_simulation_cell = get_simulation_cell(self.simulation_cell)
        wrapped = wrap_coordinates_in_z(full_simulation_cell, self.state.coordinates)
        minima = np.min(wrapped, axis=0)
        shifted_coordinates = np.subtract(wrapped, minima)
        return State(shifted_coordinates, self.state.elements, self.state.velocities)


class PostProcessingEnum(Enum):
    """Map strings to postprocessing routines"""

    num_neighbours = NumNeighboursCheck
    shift_to_origin = ShiftToOrigin
