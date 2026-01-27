# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PSR Lakehouse 🏞️🏡'
copyright = '2026, PSR'
author = 'PSR'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',     # Support for Google/NumPy style docstrings
    'sphinx.ext.viewcode',     # Add links to source code
    'sphinx.ext.intersphinx',  # Link to other projects' documentation
]

# templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


html_theme = 'shibuya'
html_static_path = ['_static']
html_theme_options = {
  "accent_color": "indigo",
  "github_url": "https://github.com/psrenergy/psr_lakehouse",
}


html_context = {
    "source_type": "github",
    "source_user": "psrenergy",
    "source_repo": "psr_lakehouse",
}