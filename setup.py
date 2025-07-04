from setuptools import setup, find_packages

setup(
    name='pgpandas',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'psycopg',
    ],
    entry_points={
        'console_scripts': [],
    },
)
