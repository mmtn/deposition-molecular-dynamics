import collections
import itertools
import logging
import os
import pickle
import sys

import yaml
from string import Template
import numpy as np


def start_logging(log_filename):
    """
    Starts logging to both stdout and given filename

    :param log_filename: path to write the log file
    """
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    log_to_file = logging.FileHandler(log_filename)
    log_to_stdout = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S"
    )
    log_to_file.setFormatter(formatter)
    log_to_stdout.setFormatter(formatter)
    logger.addHandler(log_to_file)
    logger.addHandler(log_to_stdout)
    logging.info(f"logging to {log_filename} and stdout")


def make_directories(names):
    """Creates directories from a list of names and warn user when directories already exist."""
    for name in names:
        try:
            os.mkdir(name)
        except FileExistsError:
            logging.warning(f"directory \"{name}\" already exist, check for existing data before proceeding.")


def throw_away_lines(iterator, n):
    """
    Fast way to throw away lines of data we don't need.
    Advance the iterator n-steps ahead. If n is none, consume entirely.
    """
    if n is None:
        collections.deque(iterator, maxlen=0)
    else:
        next(itertools.islice(iterator, n, n), None)


def read_yaml(filename):
    """
    Reads a YAML file to a Python dictionary object.

    :param filename: path to a YAML file
    :return: dict built from the data in YAML file
    """
    with open(filename) as file:
        return yaml.safe_load(file)


def write_yaml(filename, dictionary: dict):
    """
    Writes a Python dictionary object to a YAML file.

    :param filename: path to new YAML file
    :param dictionary: any python dict
    """
    with open(filename, "w") as file:
        yaml.dump(dictionary, file)


def read_xyz(xyz_file, step=None):
    """
    Reads data from either the first or last step of an XYZ file.

    :param xyz_file: path to XYZ file
    :param step: (default=None) reads last step when equal to None, first step when equal to 1
    :return coordinates: Nx3 numpy array for N atoms
    :return elements: Nx1 list of strings for N atoms
    :return num_atoms: int, the number of atoms (N)
    """
    # Get the number of lines in the file and the number of atoms
    header_lines_per_step = 2
    num_lines = sum(1 for _ in open(xyz_file))
    with open(xyz_file) as file:
        num_atoms = int(file.readline())
    lines_per_step = num_atoms + header_lines_per_step
    total_steps = int(num_lines / lines_per_step)

    if step is None:
        num_lines_to_skip = (lines_per_step * (total_steps - 1)) + header_lines_per_step
    elif step == 1:
        num_lines_to_skip = 0
    else:
        raise NotImplementedError("reading arbitrary step of XYZ file not implemented")

    with open(xyz_file) as file:
        throw_away_lines(file, num_lines_to_skip)
        atom_data = [line.split() for line in file]
        coordinates = [
            np.array([float(atom[1]), float(atom[2]), float(atom[3])])
            for atom in atom_data
        ]
        elements = [atom[0] for atom in atom_data]

    return coordinates, elements, num_atoms


def write_file_using_template(output_filename, template_filename, dictionary):
    """
    Generic function for using the stdlib template module to perform find and replace

    :param output_filename: path of file to write
    :param template_filename: path to plain text template
    :param dictionary: dict with key/value pairs used for find and replace
    """
    with open(template_filename) as file:
        template = Template(file.read())
        result = template.substitute(dictionary)

    with open(output_filename, "w") as file:
        file.write(result)


def read_state(pickle_location):
    """
    Reads current state of calculation from pickle file. The pickle file stores the coordinates, species (elements),
    and velocities of all simulated atoms.

    :param pickle_location: path to pickle file
    :return coordinates: Nx3 numpy array for N atoms
    :return elements: Nx1 list of strings for N atoms
    :return velocities: Nx3 numpy array for N atoms
    """
    logging.info(f"reading state from {pickle_location}")
    with open(pickle_location, "rb") as file:
        data = pickle.load(file)
    coordinates = data["coordinates"]
    elements = data["elements"]
    velocities = data["velocities"]
    return coordinates, elements, velocities


def write_state(coordinates, elements, velocities, pickle_location):
    """
    Writes current state of calculation to pickle file. The pickle file stores the coordinates, species (elements),
    and velocities of all simulated atoms.

    :param coordinates: Nx3 numpy array for N atoms
    :param elements: Nx1 list of strings for N atoms
    :param velocities: Nx3 numpy array for N atoms
    :param pickle_location: path to pickle file
    """
    logging.info(f"writing state to {pickle_location}")
    data = {
        "coordinates": coordinates,
        "elements": elements,
        "velocities": velocities
    }
    with open(pickle_location, "wb") as file:
        pickle.dump(data, file)
