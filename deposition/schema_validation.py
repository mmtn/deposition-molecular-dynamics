import logging
import re

from schema import SchemaError

DEPOSITION_TYPES = {
    "monatomic": ["deposition_element"],
    "diatomic": ["deposition_element", "diatomic_bond_length_Angstroms"],
    "molecule": ["molecule_xyz_file"],
}
# list of explicitly allowed deposition types along with conditionally required settings


def allowed_deposition_type(deposition_type):
    """
    Checks that the given deposition type is in the list of allowed types.

    Arguments:
        deposition_type (str)
    """
    if deposition_type in DEPOSITION_TYPES.keys():
        return deposition_type
    else:
        raise SchemaError(f"deposition type must be one of: {DEPOSITION_TYPES.keys()}")


def strictly_positive(number):
    """
    Checks that the number is greater than zero.

    Arguments:
        number (int or float):
    """
    if number <= 0:
        raise SchemaError("value must be greater than zero")
    return number


def reserved_keyword(value):
    """
    Allows keywords to be reserved by molecular dynamics drivers where required.

    Arguments:
        value (str): the name of the keyword to be reserved
    """
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
    template_key_regular_expression = r"[\$]([{]?[a-z,A-Z][_,a-z,A-Z,0-9]*[}]?)"
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
            raise SchemaError(f"key '{key} is used internally by {driver.name} and must be present in the template")

    # check that the template keys are populated by the input settings
    for key in template_keys:
        if key in driver.settings.keys():  # a value has been provided
            continue
        elif key in reserved_keywords:  # ignore reserved keywords
            continue
        elif key not in driver.settings.keys():  # unknown key
            raise SchemaError(f"unknown key '{key}' present in input template but has no set value")

    # check for leftover keys in the input settings that are not used in the template or elsewhere
    unused_keys = list()
    for key in driver.settings:
        if key not in template_keys and key not in driver.schema.schema:
            unused_keys.append(key)
    if len(unused_keys) > 0:
        logging.warning("unused keys detected in input file:")
        [logging.warning(f"- {key}") for key in unused_keys]
