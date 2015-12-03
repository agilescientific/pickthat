#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
Python installation file.
"""
from setuptools import setup
import re

verstr = 'unknown'
VERSIONFILE = "pickthat/_version.py"
with open(VERSIONFILE, "r") as f:
    verstrline = f.read().strip()
    pattern = re.compile(r"__version__ = ['\"](.*)['\"]")
    mo = pattern.search(verstrline)
if mo:
    verstr = mo.group(1)
    print("Version "+verstr)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

REQUIREMENTS = ['numpy',
                'matplotlib',
                'pillow',
                'shapely',
                ]

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Intended Audience :: Science/Research',
               'Natural Language :: English',
               'License :: OSI Approved :: Apache Software License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.3',
               'Programming Language :: Python :: 3.4',
               ]

setup(name='pickthat',
      version=verstr,
      description='Tools for accessing pickthis.io and analysing results.',
      url='http://github.com/agile-geoscience/pickthat',
      author='Agile Geoscience',
      author_email='hello@agilegeoscience.com',
      license='Apache 2',
      packages=['pickthat'],
      tests_require=['pytest', 'pytest-mpl'],
      install_requires=REQUIREMENTS,
      classifiers=CLASSIFIERS,
      zip_safe=False,
      )

