"""Setup script for ``rio-eval-calc``."""


import itertools as it
import os

from setuptools import setup
from setuptools import find_packages


with open('README.rst') as f:
    readme = f.read().strip()


def parse_dunder_line(string):
    """Take a line like:

        "__version__ = '0.0.8'"

    and turn it into a tuple:

        ('__version__', '0.0.8')

    Not very fault tolerant.
    """
    # Split the line and remove outside quotes
    variable, value = (s.strip() for s in string.split('=')[:2])
    value = value[1:-1].strip()
    return variable, value


with open(os.path.join('rio_eval_calc', '__init__.py')) as f:
    dunders = dict(map(
        parse_dunder_line, filter(lambda l: l.strip().startswith('__'), f)))
    version = dunders['__version__']
    author = dunders['__author__']
    email = dunders['__email__']
    source = dunders['__source__']


extras_require = {
    'dev': [
        'pytest>=3',
        'pytest-cov',
        'coveralls'
    ]
}
extras_require['all'] = extras_require['all'] = list(it.chain(*extras_require.values()))



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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    description="An alternative raster calculator for Rasterio.",
    entry_points="""
        [rasterio.rio_plugins]
        eval-calc=rio_eval_calc.core:eval_calc
    """,
    extras_require=extras_require,
    include_package_data=True,
    install_requires=[
        'click',
        'numpy>=1.10',
        'rasterio>=1.0a2',
        'str2type>=0.4'],
    keywords='Rasterio rio raster calculator plugin',
    license="New BSD",
    long_description=readme,
    packages=find_packages(exclude=['tests']),
    url=source,
    version=version,
    zip_safe=True
)
