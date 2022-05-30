import logging
import pickle

from deposition.enums import StateEnum


class State:
    """Store coordinates, elements, and velocities for a set of atoms"""

    def __init__(self, coordinates, elements, velocities):
        self.coordinates = coordinates
        self.elements = elements
        self.velocities = velocities

    def write(self, pickle_location, include_velocities=True):
        """
        Write current state to a pickle file.

        Arguments:
            pickle_location (path): path to save the pickled data to
            include_velocities (bool): whether to save velocities or not
        """
        data = {
            StateEnum.COORDINATES.value: self.coordinates,
            StateEnum.ELEMENTS.value: self.elements,
            StateEnum.VELOCITIES.value: self.velocities if include_velocities else None,
        }
        logging.info(f"writing state to {pickle_location}")
        with open(pickle_location, "wb") as file:
            pickle.dump(data, file)

    @staticmethod
    def read_state(pickle_location):
        """
        Reads current state of calculation from pickle file. The pickle file stores the
        state, species (elements),
        and velocities of all simulated atoms.

        Arguments:
            pickle_location (path): path read the pickled data from

        Returns:
            state: state, elements, velocities
        """
        logging.info(f"reading state from {pickle_location}")
        with open(pickle_location, "rb") as file:
            data = pickle.load(file)
        return State(
            data[StateEnum.COORDINATES.value],
            data[StateEnum.ELEMENTS.value],
            data[StateEnum.VELOCITIES.value],
        )
