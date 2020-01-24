#!/usr/bin/env python

from setuptools import setup

setup(name='patroni-infoblox-integration',
      version='1.1',
      description='Helper tools for maintaining ',
      author='Ants Aasma',
      author_email='ants@cybertec.at',
      url='https://github.com/cybertec-postgresql/patroni-infoblox-integration/',
      scripts=['scripts/infoblox-callback.py'],
      license='The MIT License',
      install_requires='infoblox-client')
