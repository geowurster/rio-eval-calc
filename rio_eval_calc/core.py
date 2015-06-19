"""
Core components for rio_eval_calc
"""


from __future__ import division

import affine
from collections import OrderedDict
from itertools import chain
import logging
import math
import string
from multiprocessing import Pool, cpu_count

import click
import rasterio as rio
import str2type.ext

from rio_eval_calc import __version__


logging.basicConfig()
logger = logging.getLogger('rio-eval-calc')


def window_filter(window_iter, bbox, aff):

    """
    Only yield windows that intersect the bbox.
    """

    x_min, y_min, x_max, y_max = bbox
    c_min, r_max = (x_min, y_min) * aff
    c_max, r_min = (x_max, y_max) * aff
    for window in window_iter:
        ((w_r_min, w_r_max), (w_c_min, w_c_max)) = window
        if ((w_c_min <= c_min <= w_c_max) or (w_c_min <= c_max <= w_c_max)) \
                and ((w_r_min <= r_min <= w_r_max) or (w_r_min <= r_max <= w_r_max)):
            yield window


def min_bbox(*bboxes):

    """
    Compute a minimum bounding box from a series of (xmin, ymin, xmax, ymax)
    tuples.
    """

    coords = list(chain(*bboxes))
    return min(coords[0::2]), min(coords[1::2]), max(coords[2::2]), max(coords[3::2])


def _cb_name(ctx, param, value):

    """
    Click callback to validate --name and convert it to a dict with variables
    as keys and datasources as values.
    """

    output = OrderedDict()
    if value is None:
        return output
    else:
        for pair in value:
            if '=' not in pair:
                raise click.BadParameter('Invalid syntax: {}'.format(pair))
            else:
                char, ds = pair.split('=', 1)
                if char not in list(string.ascii_letters):
                    raise click.BadParameter("Variable is not a letter: {}".format(char))
                output[char] = ds

    return output


def _cb_bbox(ctx, param, value):

    """
    Click callback for --bbox to validate.
    """

    if value is None:
        return value
    else:
        x_min, y_min, x_max, y_max = value
        if (x_min > x_max) or (y_min > y_max):
            raise click.BadParameter("self-intersection detected: {}".format(value))
        else:
            return value


def _processor(args):

    scope = {}
    for var, ds in args['input_names'].items():
        with rio.open(ds) as src:
            scope[var] = src.read(window=args['window'], boundless=True,
                                  masked=args['masked']).astype(args['calc_dtype'])

    for expr in args['expressions']:
        eval(expr, globals(), scope)

    return args['window'], scope['data']


def _cb_res(ctx, param, value):

    """
    Click callback to validate and transform --res.
    """

    if not value:
        return value
    elif len(value) == 1:
        xres = value
        yres = value
    elif len(value) == 2:
        xres, yres = value
    else:
        raise click.BadParameter("--res cannot be specified more than twice.")

    if xres < 0 or yres < 0:
        raise click.BadParameter("--res must be positive.")
    else:
        return xres, yres


@click.command(name='eval-calc')
@click.version_option(prog_name='rio-eval-calc', version=__version__)
@click.option(
    '--name', 'input_names', multiple=True, required=True, callback=_cb_name,
    help="Specify an input file with a unique short (alphas only) name for use in commands "
         "like a=tests/data/RGB.byte.tif."
)
@click.option(
    '-o', '--output', required=True,
    help="Output datasource."
)
@click.argument(
    'expressions', nargs=-1, required=True
)
# @click.option(
#     '--ro', '--read-option', 'read_options', metavar='NAME=VAL', multiple=True,
#     callback=str2type.ext.click_cb_key_val,
#     help="Keyword arguments for `src.read()`."
# )
# @click.option(
#     '--wo', '--write-option', 'write_options', metavar='NAME=VAl', multiple=True,
#     callback=str2type.ext.click_cb_key_val,
#     help="Keyword arguments for `dst.write()`."
# )
@click.option(
    '--jobs', metavar='CORES', default=1, type=click.IntRange(1, cpu_count()),
    help="Process data in parallel across N cores."
)
@click.option(
    '--driver', metavar='NAME', default='GTiff',
    help="Output driver name. (default: GTiff)"
)
@click.option(
    '-c', '--creation-option', 'creation_options', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help="Driver specific creation options."
)
@click.option(
    '--nodata', type=click.FLOAT,
    help="Nodata for output image."
)
@click.option(
    '-t', '--dtype', default=rio.float32,
    type=click.Choice(['ubyte', 'uint16', 'int16', 'uint32', 'int32', 'float32', 'float64']),
    help="Output data type. (default: Float32)"
)
@click.option(
    '--windows', 'window_ds_var', metavar='VARIABLE',
    help="Variable assigned to the datasource whose window structure should be used "
         "for reading and writing. (default: first)"
)
@click.option(
    '--calc-dtype',
    help="Convert data to this dtype on read. (default: --dtype)"
)
@click.option(
    '--bbox', nargs=4, metavar="XMIN YMIN XMAX YMAX",
    help="Only process data within the specified bounding box. "
         "(default: min bbox for all --name's)"
)
@click.option(
    '--res', multiple=True, type=click.FLOAT, metavar="XRES [YRES]",
    help="Output resolution in georeferenced units.  Specify once to set X and Y resolution "
         "to the same value or twice for different values.  (default: from first --name)"
)
@click.option(
    '--shape', metavar="ROWS COLS", nargs=2, type=click.INT,
    help="Shape of output raster in rows and columns.  Cannot be combined with --res. "
         "(default: see --res)"
)
@click.option(
    '--a-crs', help="Assign a CRS to the output datasource.  No CRS checks are performed for "
                    "the input datasources. (default: from first --name)"
)
@click.option(
    '--masked / --no-masked', is_flag=True,
    help="Evaluate expressions using masked arrays. (default: masked)"
)
@click.option(
    '--count', type=click.INT,
    help="Number of bands in the output datasource. (default: first --name)"
)
@click.pass_context
def eval_calc(ctx, input_names, output, expressions, jobs, bbox, driver, creation_options,
              nodata, dtype, window_ds_var, calc_dtype, res, shape, a_crs, masked,
              count):

    """
    Process raster data with Python syntax.
    """

    if isinstance(getattr(ctx, 'obj'), dict):
        logger.setLevel(ctx.obj.get('verbosity', 1))

    # Fail fasts
    if res and shape:
        raise click.BadParameter("Cannot combine --res and --target-size.")

    # Collect all the windows to process
    if window_ds_var is None:
        window_ds_var = list(input_names.keys())[0]
    with rio.open(input_names[window_ds_var]) as src:
        windows = [w for _, w in src.block_windows()]

    # Figure out the spatial extent of the data being processed
    if not bbox:
        bounds = []
        for ds in input_names.values():
            with rio.open(ds) as src:
                bounds.append(src.bounds)
        bbox = min_bbox(*bounds)
    x_min, y_min, x_max, y_max = bbox

    # Assemble the output metadata
    with rio.open(list(input_names.values())[0]) as src:
        first_meta = src.meta
        first_meta['bbox'] = src.bounds
        first_meta['res'] = src.res
    if res:
        width = math.ceil((x_max - y_max) / res[0])
        height = math.ceil((y_max - y_min) / res[1])
    elif shape:
        height, width = shape
    else:
        res = first_meta['res']
        height, width = (first_meta['height'], first_meta['width'])

    meta = {
        'dtype': dtype,
        'height': height,
        'width': width,
        'nodata': nodata,
        'driver': driver,
        'crs': a_crs or first_meta['crs'],
        'count': count or first_meta['count'],
        'transform': affine.Affine(res[0], 0.0, x_min,
                                   0.0, res[1], y_max)
    }
    meta.update(**creation_options)

    task_generator = (
        {
            'masked': masked,
            'window': win,
            'input_names': input_names,
            'calc_dtype': calc_dtype or dtype,
            'expressions': expressions
        } for win in window_filter(windows, bbox, meta['transform']))

    write_options = {'masked': masked}
    with rio.open(output, 'w', **meta) as dst:
        for data, window in Pool(jobs).imap_unordered(_processor, task_generator):
            
            if 'indexes' in write_options:
                pass
            elif len(data.shape) == 3:
                write_options['indexes'] = list(range(1, data.shape[0]))
            else:
                write_options['indexes'] = 1
            
            write_options['window'] = window
            dst.write(data.astype(dst.meta['dtype']), **write_options)


if __name__ == '__main__':
    eval_calc()
