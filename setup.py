#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(name='fred-logger-maintenance',
      description='NIC.CZ LOGGER-MAINTENANCE',
      author='Jan Musilek, CZ.NIC',
      author_email='jan.musilek@nic.cz',
      url='http://www.nic.cz/',
      platforms=['posix'],
      python_requires='>=3.5',
      long_description="CZ.NIC LOGGER_MAINTENANCE",
      packages=find_packages(),

      scripts=['create_parts.py', 'drop_parts.py'],

      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
      ])
