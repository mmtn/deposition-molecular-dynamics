from enum import Enum

import deposition


class DriverEnum(Enum):
    "Associate names with specific implemented driver classes"

    LAMMPS = deposition.drivers.lammps_driver.LAMMPSDriver
    GULP = deposition.drivers.gulp_driver.GULPDriver
