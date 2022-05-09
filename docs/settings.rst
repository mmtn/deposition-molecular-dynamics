.. _settings:

List of settings
----------------

A complete settings file includes:
    - all required core settings
    - subsection with all required driver settings
    - subsection with all required simulation cell settings

These settings should be written in the YAML format, e.g.::

    deposition_type: monatomic
    deposition_element: O
    ...

    driver_settings:
        name: LAMMPS
        ...

    simulation_cell:
        a: 8.08
        ...

Sample settings files can be found in the `examples` directory.

Core settings
=============

==================================  ==============  ==============  =======================
Setting                             Required        Type            Description
==================================  ==============  ==============  =======================
deposition_height_Angstroms         Yes             int/float       how far above the surface to add new atoms/molecules
deposition_temperature_Kelvin       Yes             int/float       temperature of newly added atoms/molecules
deposition_time_picoseconds         Yes             int/float       duration of the deposition simulation
deposition_type                     Yes             str             the style of deposition to perform ("monatomic" or "molecule")
driver_settings                     Yes             dict            settings for the chosen molecular dynamics driver
max_sequential_failures             Yes             int             number of failed iterations before the calculation is terminated
max_total_iterations                Yes             int             total number of iterations to run before exiting
num_deposited_per_iteration         Yes             int             number of atoms/molecules added in each iteration
position_distribution               Yes             str             name of the class for generating new positions (see :class:`here <deposition.distributions.PositionDistributionEnum>`)
relaxation_time_picoseconds         Yes             int/float       duration to simulate the system before the deposition event
simulation_cell                     Yes             dict            specification of the simulation cell
substrate_xyz_file                  Yes             path            path to an XYZ file of the initial substrate structure
velocity_distribution               Yes             str             name of the class for generating new velocities (see :class:`here <deposition.distributions.VelocityDistributionEnum>`)
velocity_distribution_parameters    Yes             list            settings for the given velocity distribution
command_prefix                      No              string          prefix to the shell command, e.g. mpiexec (default="")
log_filename                        No              path            path to use for the log file (default="deposition.log")
postprocessing                      No              dict            postprocessing routines to enable (see :class:`here <deposition.postprocessing.PostprocessingEnum>`) (default=None)
strict_postprocessing               No              bool            raises an error instead of a warning if the postprocessing fails (default=False)
deposition_element                  Conditional     str             symbol of the element to be deposited (required if deposition_type == "monatomic)
molecule_xyz_file                   Conditional     path            path to the structure of the deposited molecule (required if deposition_type == "molecule)
==================================  ==============  ==============  =======================


Driver settings
===============

All core driver settings are listed here. Additional parameters to be substituted in the input template
may also be included in this settings section.

==========================================  ==============  ==============  =======================
Setting                                     Required        Type            Description
==========================================  ==============  ==============  =======================
name                                        Yes             str             name of the class for handling simulations (see :class:`deposition.drivers.driver_enums.DriverEnum`)
path_to_binary                              Yes             path            path to the molecular dynamics binary program
path_to_input_template                      Yes             path            path to the input template for this software
velocity_scaling_from_metres_per_second     Yes             int/float       scaling factor used for generating velocities
command_line_args                           No              str             additional arguments to the software at the command line
==========================================  ==============  ==============  =======================


Simulation cell settings
========================

==================================  ==============  ==============  =======================
Setting                             Required        Type            Description
==================================  ==============  ==============  =======================
a                                   Yes             int/float       simulation cell length a (Angstroms)
b                                   Yes             int/float       simulation cell length b (Angstroms)
c                                   Yes             int/float       simulation cell length c (Angstroms)
alpha                               Yes             int/float       simulation cell angle alpha (degrees)
beta                                Yes             int/float       simulation cell angle beta (degrees)
gamma                               Yes             int/float       simulation cell angle gamma (degrees)
==================================  ==============  ==============  =======================

