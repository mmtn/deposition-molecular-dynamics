import logging
import os
import re
from enum import Enum

from schema import And, Optional, Or, Schema, SchemaError, Use

from deposition.distributions import (PositionDistributionEnum,
                                      VelocityDistributionEnum)
from deposition.enums import SettingsEnum, SimulationCellEnum


class DepositionTypeEnum(Enum):
    """List of explicitly allowed deposition types along with conditionally required settings"""

    monatomic = ["deposition_element"]
    molecule = ["molecule_xyz_file"]


def allowed_deposition_types(deposition_type):
    """Checks that the given deposition type is in the list of allowed types."""
    try:
        return DepositionTypeEnum[deposition_type].name
    except KeyError:
        raise SchemaError(
            f"deposition type must be one of: {[x.name for x in DepositionTypeEnum]}"
        )


def allowed_position_distributions(selected_distribution):
    """Checks that the position distribution is in the list of allowed distributions"""
    try:
        return PositionDistributionEnum[selected_distribution].name
    except KeyError:
        raise SchemaError(
            f"position distribution must be one of: {[x.name for x in PositionDistributionEnum]}"
        )


def allowed_velocity_distributions(selected_distribution):
    """Checks that the velocity distribution is in the list of allowed distributions"""
    try:
        return VelocityDistributionEnum[selected_distribution].name
    except KeyError:
        raise SchemaError(
            f"velocity distribution must be one of: {[x.name for x in VelocityDistributionEnum]}"
        )


def strictly_positive(number):
    """Checks that the number is greater than zero."""
    if number <= 0:
        raise SchemaError("value must be greater than zero")
    return number


def reserved_keyword(keyword):
    """Allows keywords to be reserved by molecular dynamics drivers where required."""
    raise SchemaError("this key has been reserved for internal use")


def check_input_file_syntax(driver):
    """
    Validates the syntax of the input file template.

    Variables specified by `${var}` style notation are found and checked for mismatched delimiters. Errors and warnings
    are provided when there is a mismatch between the keys provided in the settings and the variables specified in the
    template file.

    Arguments:
        driver (MolecularDynamicsDriver): driver object with a schema dictionary
    """
    # regex matches any variable placeholder starting with the $ character, either ${with} or $without braces
    template_key_regular_expression = (
        r"[\$]([{]?[a-z_plane,A-Z][_,a-z_plane,A-Z,0-9]*[}]?)"
    )
    reserved_keywords = driver.get_reserved_keywords()

    with open(driver.settings["path_to_input_template"]) as file:
        template_matched_keys = re.findall(template_key_regular_expression, file.read())

    # check for mismatched delimiters
    template_keys = list()
    for key in template_matched_keys:
        if ("{" in key and "}" not in key) or ("}" in key and "{" not in key):
            raise SchemaError(f"incomplete variable specification: {key}")
        template_keys.append(key.strip("{}"))

    # check that all internal keywords are present in the template
    for key in reserved_keywords:
        if key not in template_keys:
            raise SchemaError(
                f"key '{key} is used internally by {driver.name} and must be present in the template"
            )

    # check that the template keys are populated by the input settings
    for key in template_keys:
        if key in driver.settings.keys():  # a value has been provided
            continue
        elif key in reserved_keywords:  # ignore reserved keywords
            continue
        elif key not in driver.settings.keys():  # unknown key
            raise SchemaError(
                f"unknown key '{key}' present in input template but has no set value"
            )

    # check for leftover keys in the input settings that are not used in the template
    schema_keys = [k.schema if type(k) is Optional else k for k in driver.schema.schema]
    unused_keys = list()
    for key in driver.settings:
        if key not in template_keys and key not in schema_keys:
            unused_keys.append(key)
    if len(unused_keys) > 0:
        logging.warning("unused keys detected in input file:")
        [logging.warning(f"- {key}") for key in unused_keys]


settings_schema = Schema(
    {
        SettingsEnum.DEPOSITION_HEIGHT.value: And(
            Or(int, float), Use(strictly_positive)
        ),
        SettingsEnum.DEPOSITION_TEMPERATURE.value: And(
            Or(int, float), Use(strictly_positive)
        ),
        SettingsEnum.DEPOSITION_TIME.value: And(Or(int, float), Use(strictly_positive)),
        SettingsEnum.DEPOSITION_TYPE.value: And(str, Use(allowed_deposition_types)),
        SettingsEnum.MAX_SEQUENTIAL_FAILURES.value: And(int, Use(strictly_positive)),
        SettingsEnum.MAX_TOTAL_ITERATIONS.value: And(int, Use(strictly_positive)),
        SettingsEnum.MIN_VELOCITY.value: And(Or(int, float), Use(strictly_positive)),
        SettingsEnum.NUM_DEPOSITED_PER_ITERATION.value: And(
            int, Use(strictly_positive)
        ),
        SettingsEnum.POSITION_DISTRIBUTION.value: And(
            str, Use(allowed_position_distributions)
        ),
        SettingsEnum.RELAXATION_TIME.value: And(Or(int, float), Use(strictly_positive)),
        SettingsEnum.DRIVER_SETTINGS.value: dict,
        SettingsEnum.SIMULATION_CELL.value: dict,
        SettingsEnum.SUBSTRATE_XYZ_FILE.value: os.path.exists,
        SettingsEnum.VELOCITY_DISTRIBUTION.value: And(
            str, Use(allowed_velocity_distributions)
        ),
        Optional(SettingsEnum.COMMAND_PREFIX.value, default=""): str,
        Optional(SettingsEnum.DEPOSITION_ELEMENT.value, default=None): str,
        Optional(SettingsEnum.LOG_FILENAME.value, default="deposition.log"): str,
        Optional(SettingsEnum.MOLECULE_XYZ_FILE.value, default=None): os.path.exists,
        Optional(SettingsEnum.POSITION_DISTRIBUTION_PARAMS.value, default=[]): list,
        Optional(SettingsEnum.POSTPROCESSING.value, default=None): dict,
        Optional(SettingsEnum.STRICT_POSTPROCESSING.value, default=False): bool,
        Optional(SettingsEnum.VELOCITY_DISTRIBUTION_PARAMS.value, default=[]): list,
    }
)

simulation_cell_schema = Schema(
    {
        SimulationCellEnum.A.value: And(Or(int, float), Use(strictly_positive)),
        SimulationCellEnum.B.value: And(Or(int, float), Use(strictly_positive)),
        SimulationCellEnum.C.value: And(Or(int, float), Use(strictly_positive)),
        SimulationCellEnum.ALPHA.value: And(Or(int, float), Use(strictly_positive)),
        SimulationCellEnum.BETA.value: And(Or(int, float), Use(strictly_positive)),
        SimulationCellEnum.GAMMA.value: And(Or(int, float), Use(strictly_positive)),
    }
)


def get_settings_schema():
    """
    A list of the required and optional settings for the simulation. These settings control the type and nature of the
    deposition to be simulated.

    Note that settings for the :meth:`simulation cell <deposition.input_schema.get_simulation_cell_schema>` and
    molecular dynamics :ref:`driver <drivers>` must also be provided.

    A full list of required settings is given :ref:`here <settings>`.
    """
    return settings_schema


def get_simulation_cell_schema():
    """
    Input schema for the parameters which define the periodic cell. Lengths are in
    Angstroms and angles are in degrees.

    Example::

        a: 24     # Angstroms
        b: 24     # Angstroms
        c: 200    # Angstroms
        alpha: 90 # degrees
        beta: 90  # degrees
        gamma: 90 # degrees
    """
    return get_simulation_cell_schema
