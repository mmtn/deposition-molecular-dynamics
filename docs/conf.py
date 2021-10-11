# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../deposition'))
sys.path.insert(0, os.path.abspath('../deposition/drivers'))

# -- Project information -----------------------------------------------------

project = 'Deposition'
copyright = '2021, M. J. Cyster'
author = 'M. J. Cyster'
release = '1.0.0-alpha'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

napoleon_include_init_with_doc = True

templates_path = ['_templates']
exclude_patterns = []
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------

html_theme = 'haiku'
