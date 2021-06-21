# deposition-molecular-dynamics
Python wrapper for simulating deposition processes with molecular dynamics 

## Requirements

- Python 3.8

## Basic usage

Write a `settings.yaml` file with values for all the fields defined in the settings schema (`src/schema_definitions.py`). Include settings for the molecular dynamics driver you wish you use. You can use the settings file in the `examples/LAMMPS/settings` directory as a basis.

Ensure an XYZ file is present which defines the substrate on which to deposit.

Ensure an input template is present which will be used by the molecular dynamics software. Fields in the template written as bash style variables (`${variable_name} syntax`) will be replaced with values from the driver settings. 

Set up a virtual environment and install the required packages:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Go to the directory where you have stored your settings and substrate and run
```bash
python3 path/to/deposition.py --settings settings.yaml
```