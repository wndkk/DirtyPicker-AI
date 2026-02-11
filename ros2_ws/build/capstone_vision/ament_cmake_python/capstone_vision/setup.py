from setuptools import find_packages
from setuptools import setup

setup(
    name='capstone_vision',
    version='0.0.0',
    packages=find_packages(
        include=('capstone_vision', 'capstone_vision.*')),
)
