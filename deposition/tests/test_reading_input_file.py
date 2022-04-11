import os.path

import deposition.input_schema
import deposition.settings
import pytest
import schema
import yaml

"""
Note: validation of data types is performed by the schema package, subject to 
deposition/schema_definitions.py.
"""

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "test_data/valid_settings.yaml")
with open(SETTINGS_FILE) as file:
    VALID_SETTINGS = yaml.safe_load(file)


def validate_settings(settings=None):
    settings = settings or VALID_SETTINGS
    validated = deposition.input_schema.get_settings_schema().validate(settings)
    settings_class = deposition.settings.Settings(validated)


@pytest.fixture
def mock_missing_file(monkeypatch):
    monkeypatch.setitem(VALID_SETTINGS, "substrate_xyz_file", "missing/file")


@pytest.fixture
def mock_unknown_keyword(monkeypatch):
    monkeypatch.setitem(VALID_SETTINGS, "unknown_keyword", "unknown")


@pytest.fixture
def mock_missing_keyword(monkeypatch):
    monkeypatch.delitem(VALID_SETTINGS, "deposition_type")


def test_valid_settings():
    os.chdir(os.path.dirname(__file__))
    validate_settings()


def test_missing_file(mock_missing_file):
    with pytest.raises(schema.SchemaError):
        validate_settings()


def test_unknown_keyword(mock_unknown_keyword):
    with pytest.raises(schema.SchemaWrongKeyError):
        validate_settings()


def test_missing_keyword(mock_missing_keyword):
    with pytest.raises(schema.SchemaMissingKeyError):
        validate_settings()
