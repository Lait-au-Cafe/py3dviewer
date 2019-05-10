# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='py3dviewer', 
    version='0.1.0', 
    description='A python module to visualize 3D model data. ', 
    long_description=readme, 
    author='Lait-au-Cafe', 
    author_email='laitaucafe8@gmail.com', 
    url='https://github.com/Lait-au-Cafe/py3dviewer', 
    license=license, 
    packages=find_packages(exclude=('docs'))
)
