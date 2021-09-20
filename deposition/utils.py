import logging

import numpy as np
from pymatgen.core.lattice import Lattice
from pymatgen.io.lammps.data import lattice_2_lmpbox

from deposition import schema_definitions, schema_validation
from .drivers import GULPDriver, LAMMPSDriver


def get_simulation_cell(simulation_cell):
    """
    Read information about the simulation cell from the specified YAML file.
    Additional geometry is then calculated using routines from the `pymatgen` module
    """
    simulation_cell = schema_definitions.simulation_cell_schema.validate(simulation_cell)
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
        "lammps_box": lammps_box
    }

    simulation_cell.update(additional_geometry_information)

    return simulation_cell


def get_molecular_dynamics_driver(driver_settings, simulation_cell, deposition_time_picoseconds,
                                  relaxation_time_picoseconds):
    """
    Initialise an instance of the driver for the specified molecular dynamics software

    The instance must provide the following methods:
    - write_inputs(filename, coordinates, elements, velocities, iteration_stage)
    - read_outputs(filename)
    """
    driver_name = driver_settings["name"].upper()
    if driver_name == "GULP":
        driver = GULPDriver(driver_settings, simulation_cell)
    elif driver_name == "LAMMPS":
        driver = LAMMPSDriver(driver_settings, simulation_cell)
    else:
        raise NotImplementedError(f"specified MD driver \'{driver_settings['name']}\' not found")
    logging.info(f"Using {driver_name} for molecular dynamics")
    schema_validation.add_globally_reserved_keywords(driver)
    schema_validation.check_input_file_syntax(driver)
    driver.settings.update({"deposition_time_picoseconds": deposition_time_picoseconds})
    driver.settings.update({"relaxation_time_picoseconds": relaxation_time_picoseconds})
    return driver
