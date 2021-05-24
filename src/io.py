import collections
import itertools
import logging
import os
import pickle
import sys

import yaml
from datetime import datetime as dt
from string import Template
import numpy as np


def start_logging(log_filename):
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
    for name in names:
        try:
            os.mkdir(name)
        except FileExistsError:
            logging.warning(f"directory \"{name}\" already exist. Check for existing data before proceeding.")


def throw_away_lines(iterator, n):
    """
    Fast way to throw away lines of data we don't need.
    Advance the iterator n-steps ahead. If n is none, consume entirely.
    """
    if n is None:  # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:  # advance to the empty slice starting at position n
        next(itertools.islice(iterator, n, n), None)


def read_yaml(filename):
    with open(filename) as file:
        return yaml.full_load(file)


def read_status():
    try:
        status = read_yaml("status.yaml")
    except FileNotFoundError:
        logging.info("no status.yaml file found, making a new one")
        write_status(iteration_number=1, num_sequential_failures=0)
        return read_status()
    return int(status["iteration_number"]), int(status["num_sequential_failures"]), status["pickle_location"]


def write_status(iteration_number, num_sequential_failures, pickle_location=None):
    status = {"last_updated": dt.now(),
              "iteration_number": iteration_number,
              "num_sequential_failures": num_sequential_failures,
              "pickle_location": pickle_location}
    with open("status.yaml", "w") as file:
        yaml.dump(status, file)


def read_xyz(xyz_file, step=None):
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


def read_state(pickle_file):
    logging.info(f"reading state from {pickle_file}")
    with open(pickle_file, "rb") as file:
        data = pickle.load(file)
    coordinates = data["coordinates"]
    elements = data["elements"]
    velocities = data["velocities"]
    return coordinates, elements, velocities


def write_state(coordinates, elements, velocities, pickle_file="saved_state.pickle"):
    logging.info(f"writing state to {pickle_file}")
    data = {
        "coordinates": coordinates,
        "elements": elements,
        "velocities": velocities
    }
    with open(pickle_file, "wb") as file:
        pickle.dump(data, file)


def write_file_using_template(output_filename, template_filename, yaml_path_or_dict):
    if isinstance(yaml_path_or_dict, dict):
        dictionary = yaml_path_or_dict
    elif isinstance(yaml_path_or_dict, str):
        dictionary = read_yaml(yaml_path_or_dict)
    else:
        raise TypeError("template information must be path to yaml file or dict")

    with open(template_filename) as file:
        template = Template(file.read())
        result = template.substitute(dictionary)
    with open(output_filename, "w") as file:
        file.write(result)
