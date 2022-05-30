.. _example:

Example: oxidation of aluminium
-------------------------------

Introduction
============

This example is provided as a way to understand the process of setting up and running a deposition calculation with this
module. Here we are interested in depositing individual oxygen atoms on an aluminium substrate. In the first instance we
should choose a molecular dynamics program which will do all the heavy lifting in the calculation as well as an
interatomic potential which describes the physics we are interested in and is compatible with our chosen program. In
this example we will use `LAMMPS`_ and a ReaxFF `potential`_ developed by Hong and van Duin to describe the oxidation of
aluminium nanoparticles.

.. note::

   Molecular dynamics software is run by the `deposition` package using a driver class. This package currently provides
   drivers for :ref:`GULP <driver_GULPDriver>` and :ref:`LAMMPS <driver_LAMMPSDriver>`. To use an alternative program
   you will need to :ref:`write a new driver <new_drivers>`. To run this example you will need to have LAMMPS installed.

After due diligence to ensure the potential is suitable for our materials, we create a substrate structure of pure Al
in an 8 by 8 Angstrom supercell. In scientific work a larger substrate surface is required to avoid the impact of the
periodic boundary conditions on the results. Using the software (LAMMPS) and potential (ReaxFF) we are working with,
the substrate geometry and supercell are optimised (or relaxed) to find the minimum energy configuration. The result of
the optimisation process is used as the initial substrate for the oxidation calculation.

At this point it's a good idea to set up a directory to store all the inputs for our calculation. The initial structure
will look something like::

    examples/LAMMPS
        settings
            Hong_and_van_Duin_2015_Al_O.reaxff
            substrate.xyz

.. _LAMMPS: https://www.lammps.org/
.. _potential: https://doi.org/10.1021/acs.jpcc.5b04650


.. _example_template:

Setting up an input template
============================

The next thing we need is to provide is a template which defines how LAMMPS will run each part of the calculation. It
should look like a regular input file for the software you are using with some important differences. The template
contains variable fields which will be replaced with the chosen values for each simulation. The variables are formatted
in shell script style ${variable} syntax. These variables can take on a few forms:

- (**required**) references to input and output data files should use the `${filename}` variable
- (**required**) any variables listed as `reserved_keywords`_ by the software driver must be present
- (optional) any additional variables which are to be set from the deposition input settings

Below is the input template we will use in this example:

.. literalinclude:: ../examples/LAMMPS/settings/lammps_input_template.txt

Note the way that the `${filename}` variable is used to address input and output data. The `${num_steps}` variable is
included as it is required by the LAMMPS driver. Other variables such as `${temperature_of_system}` are do not need to
be in the template but varing simulation parameters such as temperature or timestep is easier in this case. This file
is also saved in the `settings` directory from the previous section.

.. _reserved_keywords: drivers/LAMMPSDriver.html#deposition.drivers.LAMMPSDriver.reserved_keywords


.. _example_settings:

Input settings
==============

The final step in setting up the calculation is a file describing the nature of the deposition calculation. This should
be provided as a `YAML <https://yaml.org/>`_ file. The settings file has three main sections which must be populated
with the required fields. Paths to files and folders in the settings are can be either relative or absolute.

.. note::

   To ensure this example runs on a modern desktop machine rather than a supercomputer, a number of important parameters
   have been scaled down such as the distance of the deposited oxygen from the surface and the total time of the
   simulation. This example is not scientifically useful but instructive in how to use the deposition package.

1. Deposition settings
^^^^^^^^^^^^^^^^^^^^^^

This section defines the main settings for the calculation, the physics of the deposition, the duration of each
deposition, the number of deposition events, etc. A full list of the settings required for this section can be found
`here <modules/schema_definitions.html#deposition.schema_definitions.settings_schema>`_.

.. literalinclude:: ../examples/LAMMPS/settings/settings.yaml
   :lines: 1-18

2. Driver settings
^^^^^^^^^^^^^^^^^^

This section includes settings important running the software and those specific to the chosen molecular dynamics
driver. This is also where values for any variables in the input template can be included. Some of these settings are
required in all cases (see :ref:`drivers`) and some are specific to the :ref:`LAMMPS <driver_LAMMPSDriver>` driver. To
run this example, change the `path_to_binary` setting according to where LAMMPS is installed.

.. literalinclude:: ../examples/LAMMPS/settings/settings.yaml
   :lines: 20-35

3. Simulation Cell
^^^^^^^^^^^^^^^^^^

This defines the overall size and shape of the periodic simulation cell and should be provided as a set of cell
lengths and angles.

.. literalinclude:: ../examples/LAMMPS/settings/settings.yaml
   :lines: 37-44

.. _simulation cell: modules/schema_definitions.html#deposition.schema_definitions.simulation_cell_schema
.. _driver settings: drivers/drivers.html


Running the simulation
======================

With these files in place the directory structure will look like::

    examples/LAMMPS
        settings
            Hong_and_van_Duin_2015_Al_O.reaxff
            lammps_input_template.txt
            settings.yaml
            substrate.xyz

Now, from the `examples/LAMMPS` directory, we can run the calculation:

.. code-block:: bash

   source venv/bin/activate
   cd examples/LAMMPS
   python3 ../../run_deposition.py --settings settings/settings.yaml

When the calculation starts, a number of files and folders will be created. The iteration being calculated is stored in
the `current` directory and when finished the data is moved to either `iterations` or `failed` depending on whether any
issues were encountered. As the calculation proceeds a log will print in the terminal.

.. note::

   If the deposition does not finish the total number of iterations requested in the settings, running the simulation
   again will restart from the most recent iteration (based on the values recorded in the file `status.yaml`). To start
   a calculation from the beginning, delete the `status.yaml` file.
