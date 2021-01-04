# -*- coding: utf-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
r"""
Define the command line interface.

.. click:: xlref.cli:cli
   :prog: xlref
   :show-nested:

"""
import click
import logging
import click_log
import schedula as sh
import xlref
from xlref._version import __version__

log = logging.getLogger('xlref.cli')


class _Logger(logging.Logger):
    def setLevel(self, level):
        super(_Logger, self).setLevel(level)
        frmt = "%(asctime)-15s:%(levelname)5.5s:%(name)s:%(message)s"
        logging.basicConfig(level=level, format=frmt)
        rlog = logging.getLogger()
        # because `basicConfig()` does not reconfig root-logger when re-invoked.
        rlog.level = level
        logging.captureWarnings(True)


logger = _Logger('cli')
click_log.basic_config(logger)
_process = sh.SubDispatch(xlref.dsp, ['written'], output_type='value')


@click.group(
    'xlref', context_settings=dict(help_option_names=['-h', '--help'])
)
@click.version_option(__version__)
def cli():
    """
    xlref command line tool.
    """


@cli.command('read', short_help='Read xlref data excel references.')
@click.argument('output-file', type=click.Path(writable=True), nargs=1)
@click.argument('input-reference', nargs=-1)
@click.option(
    '-F', '--input-file', help='JSON xlref data excel references.',
    show_default=True, multiple=True
)
@click_log.simple_verbosity_option(logger)
def read(output_file, input_file, input_reference):
    """
    Read recursively the list of xlref data excel references.

    OUTPUT_FILE: output file (format: .json).

    INPUT_REFERENCE: xlref data excel reference.
    """
    return _process({
        'input_references': input_reference, 'input_fpaths': input_file,
        'output_fpath': output_file
    })


if __name__ == '__main__':
    cli()
