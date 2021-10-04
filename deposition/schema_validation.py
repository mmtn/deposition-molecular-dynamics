import logging
import re

from schema import Optional, Schema, SchemaError, Use

ALLOWED_DEPOSITION_TYPES = [
    "monatomic",
    "diatomic",
]
# list of explicitly allowed deposition types

GLOBALLY_RESERVED_KEYWORDS = [
    "filename",
]
# template keywords which are used internally


def allowed_deposition_type(deposition_type):
    """
    Checks that the given deposition type is in the list of allowed types.

    Arguments:
        deposition_type (str)
    """
    if deposition_type in ALLOWED_DEPOSITION_TYPES:
        return deposition_type
    else:
        raise SchemaError(f"deposition type must be one of: {ALLOWED_DEPOSITION_TYPES}")


def strictly_positive(number):
    """
    Checks that the number is greater than zero.

    Arguments:
        number (int or float):
    """
    if number <= 0:
        raise SchemaError("value must be greater than zero")
    return number


# noinspection PyUnusedLocal
def reserved_keyword(value):
    """
    Allows keywords to be reserved by molecular dynamics drivers where required.

    Arguments:
        value (str): the name of the keyword to be reserved
    """
    raise SchemaError("this key has been reserved for internal use")


def get_driver_reserved_keywords(driver):
    """
    Find keywords reserved by the molecular dynamics driver.

    Arguments:
        driver (MolecularDynamicsDriver): driver object with a schema dictionary

    Returns:
        reserved_keywords (list): keywords reserved by the driver
    """
    reserved_keywords = list()
    for key, value in driver.schema_dictionary.items():
        if type(value) is Use and value._callable.__name__ == "reserved_keyword":
            reserved_keywords.append(key.schema)
    return reserved_keywords


def add_globally_reserved_keywords(driver):
    """
    Adds globally reserved keywords to the keywords of the driver.

    Arguments:
        driver (MolecularDynamicsDriver): driver object with a schema dictionary
    """
    for key in GLOBALLY_RESERVED_KEYWORDS:
        driver.schema_dictionary.update({Optional(key): Use(reserved_keyword)})
    schema = Schema(driver.schema_dictionary, ignore_extra_keys=True)
    schema.validate(driver.settings)


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

    with open(driver.settings["path_to_input_template"]) as file:
        template_matched_keys = re.findall(template_key_regular_expression, file.read())

    template_keys = list()
    for key in template_matched_keys:
        if ("{" in key and "}" not in key) or ("}" in key and "{" not in key):  # check for mismatched delimiters
            raise SchemaError(f"incomplete variable specification: {key}")
        template_keys.append(key.strip("{}"))

    for key in template_keys:
        if key in driver.settings.keys():  # a value has been provided
            continue
        elif key in get_driver_reserved_keywords(driver):  # ignore reserved keywords
            continue
        elif key not in driver.settings.keys():  # unknown key
            raise SchemaError(f"unknown key '{key}' present in input template but has no set value")

    # check for keys in the input file that are not used in the template or elsewhere
    unused_keys = list()
    for key in driver.settings:
        if key not in template_keys and key not in driver.schema.schema:
            unused_keys.append(key)
    if len(unused_keys) > 0:
        logging.warning("unused keys detected in input file:")
        for key in unused_keys:
            logging.warning(f"- {key}")
