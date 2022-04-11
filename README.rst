deposition
----------

.. warning::

   This repository is not maintained! It is freely available (licensed under GNU
   `GPLv3`_) in the hopes that it will be useful to someone. If you do find this
   project useful in your work, please cite the `paper`_ for which it was developed.

   .. _paper: https://doi.org/10.1038/s41534-020-00360-4
   .. _GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html

A Python wrapper for simulating deposition processes with molecular dynamics.

Requirements
============

- Python 3.8

Installation
============

Clone the repository::

    git clone https://github.com/mmtn/deposition-molecular-dynamics.git

Create a virtual environment and install the required packages::

    cd deposition-molecular-dynamics
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install .

Build the documentation::

    sphinx-build -b html docs html-docs

The docs can then be accessed by opening `html-docs/index.html` in your browser. Sphinx
can also build the documentation in plain text, as a PDF using LaTeX, or in other ways.
Various other `builders`_ are available

.. _builders: https://www.sphinx-doc.org/en/master/usage/builders/index.html

Structure of the code
=====================

It is helpful to understand the layout of the code to use it most effectively. The
primary object which manages the simulation is the :doc:`Deposition <classes/Deposition>`
class. It is responsible for creating the directories where calculation data will be
kept, transferring data between iterations, and keeping track of how many iterations
have been performed and how many have failed. The `Deposition` class will also
initialise a molecular dynamics :doc:`driver <drivers/drivers>`. In the input settings,
the name of a driver must be specified. This driver is responsible for interfacing with
a particular molecular dynamics software, e.g. LAMMPS, GULP, etc. It moves data between
the ongoing deposition calculation and the software.

A deposition calculation consists of multiple iterations. The
:doc:`Iteration <classes/Iteration>` class represents one cycle of relaxing the system
before depositing an atom or molecule as specified by the input settings. The
`subprocess` library is used to run the molecular dynamics software.

Each iteration consists of the following steps:

    - relaxation: simulation at the specified temperature to equilibrate the system
    - deposition: simulation of the introduction of a new atom or molecule
    - finalisation: the final simulation state is analysed and the data is stored

In the finalisation stage each iteration is assessed to be either a success or a
failure using :doc:`postprocessing <modules/postprocessing>` routines. It is possible to
code your own routines to check for success or failure. Successful iterations are stored
in a directory and the final state of the iteration is used as the initial state of the
following iteration. Failed iterations are stored in a different directory and the
calculation returns to the state before the failed iteration.

The calculation is finalised when either the total number of iterations or the maximum
number of failed iterations is exceeded.

.. note::

   To run the software in parallel you can specify a `command_prefix` in the settings
   such as "`mpiexec`". This will be prepended to the command for every molecular
   dynamics simulation.

Usage
=====

The settings for the deposition simulation should be specified in a `YAML`_ file. The
full list of inputs can be seen :doc:`here <settings>`. This should include settings
for the molecular dynamics :doc:`driver <drivers/drivers>` you wish to use. A detailed
:ref:`example <example>` is available.

The initial state of the system before anything has been deposited must be provided in
an XYZ file which is specified in the input settings.

You must also provided an input template which will be used to create input files for
the molecular dynamics software. In the template, fields which are written as bash style
variables (`${variable_name}` syntax) will be replaced with values from the driver
settings. You can use this to implement variable temperature, timestep, etc. An example
LAMMPS input template can be found :ref:`here <example_template>`.

.. _YAML: https://yaml.org/

.. note::

   The `${filename}` variable is reserved and must be placed in the template for the
   names of any input and output files. For example, in the LAMMPS input template the
   final state is written using the command `write_data ${filename}.output_data`.

To summarise, the following files are required:

    - calculation settings specified in YAML file
    - the initial atomic structure specified in XYZ file
    - an input template for the given molecular dynamics software

Once these requirements are satisfied the `run_deposition.py` script can be used to
start the deposition from the command line. In directory where you have stored your
settings and substrate, run::

    python3 path/to/run_deposition.py --settings settings/settings.yaml

Alternatively you can start a simulation from your own Python script::

    import deposition

    settings = deposition.read_settings_from_file(settings_filename)
    calculation = deposition.Deposition(settings)
    calculation.run()


Customisation and contributing
==============================

The package is designed to be extended by the end user. The structure allows for
and encourages the implementation of new routines for:

    - interacting with alternative molecular dynamics software
    - the positioning of new atoms/molecules
    - the velocities of new atoms/molecules
    - postprocessing of the structure following each deposition

More information about how to make these additions is :ref:`here <contributing>`.