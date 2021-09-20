# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import os
import sys

# import deposition
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../deposition'))
sys.path.insert(0, os.path.abspath('../deposition/drivers'))

# -- Project information -----------------------------------------------------

project = 'Deposition'
copyright = '2021, M. J. Cyster'
author = 'M. J. Cyster'
release = '0.02'

# -- General configuration ---------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.viewcode']
templates_path = ['_templates']
exclude_patterns = []
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------

html_theme = 'haiku'
html_static_path = ['_static']
