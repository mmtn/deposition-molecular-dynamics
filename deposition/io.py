import collections
import itertools
import logging
import os
import sys
from string import Template

import numpy as np

from deposition.enums import DirectoriesEnum
from deposition.state import State


def start_logging(log_filename):
    """
    Starts logging to both stdout and given filename

    Arguments:
        log_filename (path): where to write the log file
    """
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    log_to_file = logging.FileHandler(log_filename)
    log_to_stdout = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] "
        "%(message)s",
        datefmt="%a %d %b %Y %H:%M:%S",
    )
    log_to_file.setFormatter(formatter)
    log_to_stdout.setFormatter(formatter)
    logger.addHandler(log_to_file)
    logger.addHandler(log_to_stdout)
    logging.info(f"logging to {log_filename} and stdout")


def make_directories(directory_names):
    """
    Creates directories from a list of names and logs warning instead of error when
    directories already exist.

    Arguments:
        directory_names (tuple): list of directory names to be created
    """
    for name in directory_names:
        try:
            os.mkdir(name)
            logging.info(f"created directory '{name}'")
        except FileExistsError as error:
            logging.warning(
                f"directory '{name}' already exists, check for existing data"
            )
            raise FileExistsError(
                f"remove the following directories to proceed: {[directory.value for directory in DirectoriesEnum]}"
            )


def throw_away_lines(iterator, n):
    """
    A fast way to throw away data we don't need. Advance the iterator n-steps ahead.
    If n is None, consume entirely.

    Arguments:
        iterator (path/iterable object): open file or other iterable object which
        handles the next() method
        n (int): the number of lines/iterations to discard
    """
    if n is None:
        collections.deque(iterator, maxlen=0)
    else:
        next(itertools.islice(iterator, n, n), None)


def read_xyz(xyz_file, step=None):
    """
    Reads data from either the first or last step of an XYZ file.

    Arguments:
        xyz_file (path): path to XYZ file
        step (default=None): reads the final step when None, first step when
        equal to 1

    Returns:
        state: state, elements, velocities
    """
    # Get the number of lines in the file and the number of atoms
    num_lines = sum(1 for _ in open(xyz_file))
    with open(xyz_file) as file:
        num_atoms = int(file.readline())

    header_lines_per_step = 2
    lines_per_step = num_atoms + header_lines_per_step
    total_steps = int(num_lines / lines_per_step)

    if step is None:
        num_lines_to_skip = (lines_per_step * (total_steps - 1)) + header_lines_per_step
    else:
        num_lines_to_skip = (lines_per_step * (step - 1)) + header_lines_per_step

    with open(xyz_file) as file:
        throw_away_lines(file, num_lines_to_skip)
        atom_data = [line.split() for ii, line in enumerate(file) if ii < num_atoms]
        coordinates = [
            np.array([float(atom[1]), float(atom[2]), float(atom[3])])
            for atom in atom_data
        ]
        elements = [atom[0] for atom in atom_data]

    if len(atom_data) != num_atoms:
        raise IOError(f"error reading step {step} of {xyz_file}")

    return State(np.array(coordinates), elements, velocities=None)


def write_file_using_template(output_filename, template_filename, template_values):
    """
    Uses the stdlib template module to perform find and replace in the provided
    template and write a new file.

    Arguments:
        output_filename (path): path to new file written with the template fields replaced
        template_filename (path): path to template with replaceable fields
        template_values (dict): key/value pairs used for find and replace in the
    """
    with open(template_filename) as file:
        template = Template(file.read())
        result = template.substitute(template_values)
    with open(output_filename, "w") as file:
        file.write(result)
