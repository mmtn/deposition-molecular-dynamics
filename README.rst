deposition-molecular-dynamics
=============================

A Python wrapper for simulating deposition processes with molecular dynamics.

Requirements
------------

- Python 3.8

Basic usage
-----------

Write a `settings.yaml` file with values for all the fields defined in the settings :doc:`schema <schema>`.
This should include settings for the molecular dynamics driver you wish you use.
You can use the file `examples/LAMMPS/settings/settings.yaml` as an example.

Ensure an XYZ file is present which defines the substrate on which to deposit.

Ensure an input template is present which will be used by the molecular dynamics software.
Fields in the template which are written as bash style variables (`${variable_name}` syntax) will be replaced with
values from the driver settings.

Set up a virtual environment and install the required packages::

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

We can then use the `run_deposition.py` script to start the deposition directly from the command line.
Go to the directory where you have stored your settings and substrate and run::

    python3 path/to/run_deposition.py --settings settings.yaml

Alternatively you can start the simulation from your own Python script like so::

    import deposition

    settings = deposition.read_settings_from_file(settings_filename)
    calculation = deposition.Deposition(settings)
    calculation.run()

