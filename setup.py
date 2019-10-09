from distutils.core import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()


setup(name='mereswine',
      version='1.0-rc1',
      url='https://github.com/indico/mereswine',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements,
      entry_points={'console_scripts': ['mereswine = mereswine.cli:cli']})
