#!/usr/bin/env python


"""
Setup script for rio-eval-calc
"""


import os
from setuptools import setup
from setuptools import find_packages


with open('README.rst') as f:
    readme = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('rio_eval_calc', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break


setup(
    name='rio-eval-calc',
    author=author,
    author_email=email,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    description="A raster calculator rasterio CLI plugin built on eval().",
    entry_points="""
        [rasterio.rio_commands]
        eval_calc=rio_eval_calc.core:eval_calc
    """,
    extras_require={
        'test': ['pytest', 'pytest-cov']
    },
    include_package_data=True,
    install_requires=['click>=0.3', 'rasterio'],
    keywords='Rasterio rio raster calculator plugin',
    license="New BSD",
    long_description=readme,
    packages=find_packages(),
    url=source,
    version=version,
    zip_safe=True
)
