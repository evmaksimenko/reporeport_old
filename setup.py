import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "reporeport",
    version = "0.1",
    author = "Eugenii Maksimenko",
    author_email = "eugene.maksimenko@gmail.com",
    description = ("Repository Reporter library"),
    license = "GNU GPL",
    url = "https://github.com/evmaksimenko/reporeport",
    packages=['reporeport'],
    long_description=read('README.md'),
    install_requires=['nltk>=3.0'],
    python_requires='>=3.0'
)
