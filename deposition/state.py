import logging
import pickle


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
            "coordinates": self.coordinates,
            "elements": self.elements,
            "velocities": self.velocities if include_velocities else None,
        }
        logging.info(f"writing state to {pickle_location}")
        with open(pickle_location, "wb") as file:
            pickle.dump(data, file)
