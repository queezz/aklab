#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
from aklab import __version__

# module

setup(
    name="aklab",
    version=__version__,
    author="AK",
    author_email="queezz@gmail.com",
    description=("AK lab tools"),
    license="BSD 3-clause",
    keywords="qms",
    url="https://github.com/queezz/aklab",
    packages=["aklab"],
    package_dir={"aklab": "aklab"},
    py_modules=["aklab.__init__"],
    # test_suite="testings",
    install_requires="""
        numpy>=1.10
        matplotlib>=3.0
        pandas>=1.3
        xarray
        statsmodels
      """,
    package_data={"": ["notex.mplstyle"]},
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)

