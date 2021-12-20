import logging

import numpy as np
import yaml
from pymatgen.core.lattice import Lattice
from pymatgen.io.lammps.data import lattice_2_lmpbox

from deposition import drivers, enums, schema_definitions, schema_validation


def get_simulation_cell(simulation_cell):
    """
    Additional geometry of the simulation cell is calculated using routines from the `pymatgen` module including bounds
    specification for use with LAMMPS and the cell vectors.

    Arguments:
        simulation_cell (dict): simulation cell settings (see
                                :meth:`format <deposition.schema_definitions.simulation_cell_schema>`).
    Return:
        simulation_cell (dict): updated simulation cell with added keys for additional geometry
    """
    simulation_cell = schema_definitions.simulation_cell_schema.validate(
        simulation_cell
    )
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
    Initialises one of the available molecular dynamics drivers. For more information about drivers see
    :ref:`here <drivers>`.

    Arguments:
        driver_settings (dict): settings for the specified driver, the `name` key chooses which driver is loaded
        simulation_cell (dict): specifies the size and shape of the simulation cell
        deposition_time_picoseconds (int or float): amount of time to run the deposition stage of each iteration
        relaxation_time_picoseconds (int or float): amount of time to run the relaxation stage of each iteration

    Returns:
        driver (MolecularDynamicsDriver): driver object
    """
    chosen_driver = driver_settings["name"]
    simulation_cell_full = get_simulation_cell(simulation_cell)

    if chosen_driver == "LAMMPS":
        driver_class = drivers.lammps_driver.LAMMPSDriver
    elif chosen_driver == "GULP":
        driver_class = drivers.gulp_driver.GULPDriver
    else:
        raise ValueError(f"no driver with the name '{chosen_driver}' was found")

    driver = driver_class(driver_settings, simulation_cell_full)

    schema_validation.check_input_file_syntax(driver)
    driver.settings.update({"deposition_time_picoseconds": deposition_time_picoseconds})
    driver.settings.update({"relaxation_time_picoseconds": relaxation_time_picoseconds})
    logging.info(f"Using driver for {chosen_driver}")

    return driver


def read_settings_from_file(settings_filename):
    """
    Read and validate a YAML file containing simulation settings.

    Arguments:
        settings_filename (path): path to a YAML file containing settings for the simulation

    Returns:
        settings (dict): validated settings for the deposition simulation
    """
    with open(settings_filename) as file:
        settings = yaml.safe_load(file)
    settings = schema_definitions.get_settings_schema().validate(settings)

    for requirement in schema_validation.DEPOSITION_TYPES[
        settings[enums.SettingsEnum.DEPOSITION_TYPE.value]
    ]:
        assert requirement in settings.keys(), (
            f"{requirement} required in "
            f"{settings[enums.SettingsEnum.DEPOSITION_TYPE.value]} deposition "
        )

    return settings
