========
Cookbook
========

Basic Landsat 8 Color Correction
--------------------------------

.. code-block:: console

    $ rio \
        eval-calc \
        --jobs 8 \
        --name red=LC80160332015140LGN00_B4.TIF \
        --name green=LC80160332015140LGN00_B3.TIF \
        --name blue=LC80160332015140LGN00_B2.TIF \
        --name cloud=LC80160332015140LGN00_B9.TIF \
        "np.array([red[0] - cloud[0], green[0] - cloud[0], blue[0] - cloud[0]])" \
        -o RGB.tif \
        -c COMPRESS=DEFLATE \
        -c INTERLEAVE=BAND \
        -c BIGTIFF=YES \
        -c TILED=YES \
        -c PREDICTOR=2
