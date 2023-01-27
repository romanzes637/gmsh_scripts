# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

# -- Project information -----------------------------------------------------

project = 'gmsh_scripts'
copyright = '2023, romanzes637'
author = 'romanzes637'

# The full version, including alpha/beta/rc tags
release = '0.3.3'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
'sphinx.ext.autodoc',  # Core library for html generation from docstrings
'sphinx.ext.autosummary',   # Create neat summary tables
'autoapi.extension',
'sphinx.ext.napoleon',
'sphinx_rtd_theme'
]

# PDF
# pdf_documents = [('index', u'rst2pdf', u'Sample rst2pdf doc', u'Your Name'),]
# pdf_stylesheets = ['twocolumn']

# LATEX
latex_documents = [
 ('index', 'index.tex', u'gmsh scripts', u'', 'manual'),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# AutoApi
autoapi_type = 'python'
autoapi_dirs = ['../../gmsh_scripts']
autoapi_generate_api_docs = True
# autoapi_ignore = ['*migrations*', '*test*']
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_file_patterns = ['*.py', '*.pyi']

# Internationalization
locale_dirs = ['../locale/']   # path is example but recommended
gettext_compact = False     # optional
# language = 'ru'

# Autodoc
# autosummary_generate = True
#
# autodoc_default_options = {
#     'members': True,
#     # The ones below should be optional but work nicely together with
#     # example_package/autodoctest/doc/source/_templates/autosummary/class.rst
#     # and other defaults in sphinx-autodoc.
#     'show-inheritance': True,
#     'inherited-members': True,
#     'no-special-members': True,
# }

