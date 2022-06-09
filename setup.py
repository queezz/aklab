#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
import re
import os
import sys

# load version form _version.py
VERSIONFILE = "aklab/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# module

setup(
    name="aklab",
    version=verstr,
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
      """,
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

