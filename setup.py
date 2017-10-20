#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(name='fred-logger-maintenance',
      description='NIC.CZ LOGGER-MAINTENANCE',
      author='Jan Musilek, CZ.NIC',
      author_email='jan.musilek@nic.cz',
      url='http://www.nic.cz/',
      license='GNU GPL',
      platforms=['posix'],
      python_requires='>=3.5',
      long_description="CZ.NIC LOGGER_MAINTENANCE",
      packages=find_packages(),
      )
