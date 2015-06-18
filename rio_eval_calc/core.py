"""
Core components for rio_eval_calc
"""


import logging
from multiprocessing import Pool, cpu_count

import click
import rasterio as rio
import str2type.ext

from rio_eval_calc import __version__


logging.basicConfig()
logger = logging.getLogger('rio-eval-calc')



def _processor(args):
    expressions = args['expressions']
    infile = args['infile']
    window = args['window']
    read_options = args['read_options']
    read_options.update(window=window)
    with rio.open(infile) as src:
        data = src.read(**read_options)
        scope = {
            'data': data
        }
        for expr in expressions:
            scope['data'] = eval(expr, globals(), scope)

        return window, scope['data']


@click.command(name='eval-calc')
@click.version_option(prog_name='rio-eval-calc', version=__version__)
@click.argument('infile', required=True)
@click.argument('outfile', required=True)
@click.option(
    '--ro', '--read-option', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help="Keyword arguments for `read()`."
)
@click.option(
    '--wo', '--write-option', metavar='NAME=VAl', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help="Keyword arguments for `write()`."
)
@click.option(
    '--jobs', metavar='CORES', default=1, type=click.IntRange(1, cpu_count()),
    help="Process data in parallel across N cores."
)
@click.option(
    '--count', type=click.INT,
    help="Number of bands in the output image."
)
@click.option(
    '--dtype', metavar='TYPE', help="Output data type."
)
@click.option(
    '--driver', metavar='NAME', default='GTiff', help="Output driver name. (default: GTiff)"
)
@click.option(
    '-c', 'creation_options', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help="Driver specific creation options."
)
@click.option(
    '--nodata', type=click.FLOAT,
    help="Nodata for output image."
)
@click.option(
    '--expr', 'expressions', multiple=True,
    help="Expression to evaluate."
)
@click.pass_context
def eval_calc(ctx, infile, outfile, read_option, write_option, count, dtype,
              driver, nodata, creation_options, expressions, jobs):

    """
    Process raster data with Python syntax.
    """

    if isinstance(getattr(ctx, 'obj'), dict):
        logger.setLevel(ctx.obj.get('verbosity', 1))

    with rio.open(infile) as src:
        meta = {
            'height': src.height,
            'width': src.width,
            'count': count or src.count,
            'transform': src.affine,
            'crs': src.crs,
            'driver': driver,
            'dtype': dtype or src.meta['dtype'],
            'nodata': nodata,
        }
        meta.update(**creation_options)
        with rio.open(outfile, 'w', **meta) as dst:
            task_generator = (
                {
                    'window': win,
                    'read_options': read_option,
                    'expressions': expressions,
                    'infile': infile
                } for _, win in src.block_windows())
            for win, data in Pool(jobs).imap_unordered(_processor, task_generator):
                write_option.update(window=win)
                dst.write(data.astype(dst.meta['dtype']), **write_option)


if __name__ == '__main__':
    eval_calc()
