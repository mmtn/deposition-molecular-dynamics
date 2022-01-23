import numpy as np

from deposition.state import State
from deposition.structural_analysis import wrap_coordinates_in_z
from deposition.utils import generate_neighbour_list, get_simulation_cell


def run(name, arguments, state, simulation_cell, dry_run=False):
    """
    Runs the postprocessing check on the provided structural data.

    Args:
        name: the string referring to the check
        arguments: any arguments required for the check
        state: coordinates, elements, velocities
        simulation_cell: size and shape of the simulation cell
        dry_run: optionally skip the actual check (for validation at initialisation)
    """
    if name == "num_neighbours":
        routine = NumNeighboursCheck(arguments, state, simulation_cell)
    elif name == "shift_to_origin":
        routine = ShiftToOrigin(arguments, state, simulation_cell)
    else:
        raise ValueError(f"unknown post processing routine {name}")

    if not dry_run:
        return routine.run()


class NumNeighboursCheck:
    """
    Assess the number of neighbours of all simulated atoms to check that everything is
    bonded together and there are no isolated regions.
    """

    num_arguments = 2

    def __init__(self, arguments, state, simulation_cell):
        assert (
            len(arguments) == self.num_arguments
        ), f"{self.__class__} requires {self.num_arguments} argument(s)"
        self.min_neighbours = float(arguments[0])
        self.bonding_cutoff = float(arguments[1])
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
    Assess the number of neighbours of all simulated atoms to check that
    everything is
    bonded together and there are no isolated regions.
    """

    def __init__(self, arguments, state, simulation_cell):
        assert arguments == True, "to turn on this routine, use shift_to_origin: True"
        self.state = state
        self.simulation_cell = simulation_cell

    def run(self):
        """Moves the given coordinates back to the origin at (0, 0, 0)"""
        full_simulation_cell = get_simulation_cell(self.simulation_cell)
        wrapped = wrap_coordinates_in_z(full_simulation_cell, self.state.coordinates)
        minima = np.min(wrapped, axis=0)
        shifted_coordinates = np.subtract(wrapped, minima)
        return State(shifted_coordinates, self.state.elements, self.state.velocities)
