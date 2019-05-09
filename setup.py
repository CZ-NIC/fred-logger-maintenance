#!/usr/bin/env python3
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
