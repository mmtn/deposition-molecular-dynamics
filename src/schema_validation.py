import logging
import re
from schema import Schema, SchemaError, Use, Optional


ALLOWED_DEPOSITION_TYPES = [
    "monatomic",
    "diatomic",
]

GLOBALLY_RESERVED_KEYWORDS = [
    "filename",
]


def allowed_deposition_type(deposition_type):
    if deposition_type in ALLOWED_DEPOSITION_TYPES:
        return deposition_type
    else:
        raise SchemaError(f"deposition type must be one of: {ALLOWED_DEPOSITION_TYPES}")


def strictly_positive(number):
    if number <= 0:
        raise SchemaError("value must be greater than zero")
    return number


def reserved_keyword(value):
    raise SchemaError("this key has been reserved for internal use")


def get_driver_reserved_keywords(driver):
    reserved_keywords = list()
    for key, value in driver.schema_dictionary.items():
        if type(value) is Use and value._callable.__name__ == "reserved_keyword":
            reserved_keywords.append(key.schema)
    return reserved_keywords


def add_globally_reserved_keywords(driver):
    for key in GLOBALLY_RESERVED_KEYWORDS:
        driver.schema_dictionary.update({Optional(key): Use(reserved_keyword)})
    schema = Schema(driver.schema_dictionary, ignore_extra_keys=True)
    schema.validate(driver.settings)


def check_input_file_syntax(driver):
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
        if key in get_driver_reserved_keywords(driver):  # ignore reserved keywords
            continue
        elif key in driver.settings.keys():  # a value has been provided
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

