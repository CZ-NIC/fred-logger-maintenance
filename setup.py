#!/usr/bin/env python3
#
# Copyright (C) 2017-2019  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

import os

from setuptools import find_packages, setup


def readme():
    """Return content of README file."""
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(name='fred-logger-maintenance',
      description='FRED utilities: Scripts for audit-log database maintanence',
      author='Jan Musilek, CZ.NIC',
      author_email='jan.musilek@nic.cz',
      url='http://www.nic.cz/',
      platforms=['posix'],
      python_requires='>=3.5',
      long_description=readme(),
      long_description_content_type='text/markdown',
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
