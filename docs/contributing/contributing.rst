.. _contributing:

Contributing to the code
========================

To make formal contributions, create a new git branch in your local copy of the repository called
`feature/YOUR_NEW_FEATURE`. After developing and testing your code locally, make a pull request for
the feature to be merged into the `develop` branch. Once stable, these features will be included in
the `main` branch for general use.

The structure of the package allows for additions in the following areas with relative ease.

.. toctree::
   :maxdepth: 1

   new_drivers
   distributions
   postprocessing

After making modifications to the code through adding new routines, run the following commands::

    black .
    isort .
    python -m pytest

The first two commands will ensure standardisation of code formatting. The tests will check that the new code
contains the necessary methods and that the functions are returning appropriate variable types.