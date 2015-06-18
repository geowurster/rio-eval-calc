=============
rio-eval-calc
=============

.. image:: https://travis-ci.org/geowurster/rio-eval-calc.svg?branch=master
    :target: https://travis-ci.org/geowurster/rio-eval-calc?branch=master

.. image:: https://coveralls.io/repos/geowurster/rio-eval-calc/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/rio-eval-calc?branch=master

A `rasterio <https://github.com/mapbox/rasterio>`_CLI plugin based on ``eval()`` with more freedom and access to external libraries.

Under development.  Definitely try it out but don't get too attached to anything.


Usage
-----

.. code-block:: console

    Usage: rio eval-calc [OPTIONS] INFILE OUTFILE

      Process raster data with Python syntax.

    Options:
      --version                      Show the version and exit.
      --ro, --read-option NAME=VAL   Keyword arguments for `read()`.
      --wo, --write-option NAME=VAl  Keyword arguments for `write()`.
      --jobs CORES                   Process data in parallel across N cores.
      --count INTEGER                Number of bands in the output image.
      --dtype TYPE                   Output data type.
      --driver NAME                  Output driver name. (default: GTiff)
      -c NAME=VAL                    Driver specific creation options.
      --nodata FLOAT                 Nodata for output image.
      --expr TEXT                    Expression to evaluate.
      --help                         Show this message and exit.


Installing
----------

.. code-block:: console

    $ git clone https://github.com/geowurster/rio-eval-calc
    $ pip install rio-eval-calc/


Developing
----------

.. code-block:: console

    $ git clone https://github.com/geowurster/rio-eval-calc
    $ cd rio-eval-calc
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .[test]
    $ py.test tests --cov rio_eval_calc --cov-report term-missing


License
-------

See ``LICENSE.txt``.
