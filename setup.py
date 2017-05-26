from distutils.core import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()


setup(name='cephalopod',
      version='1.0',
      url='https://github.com/indico/cephalopod',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements
      )
