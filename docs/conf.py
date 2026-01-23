# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PSR Lakehouse'
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

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'description': 'Python client for PSR data lakehouse API',
    'fixed_sidebar': True,
    'page_width': '1400px',
    'sidebar_width': '300px',
    'body_text': '#333333',
    'link': '#2980b9',
    'link_hover': '#1f5c7d',
    'sidebar_link': '#2980b9',
    'sidebar_link_underscore': '#2980b9',
    'gray_1': '#f8f8f8',
    'gray_2': '#e8e8e8',
    'gray_3': '#d8d8d8',
    'note_bg': '#e7f2fa',
    'note_border': '#2980b9',
    'warn_bg': '#fff4e6',
    'warn_border': '#f39c12',
    'github_user': 'psrenergy',
    'github_repo': 'psr_lakehouse',
    'github_button': False,
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# Add custom CSS
html_css_files = [
    'custom.css',
]

# Add custom JavaScript
html_js_files = [
    'theme-toggle.js',
]
