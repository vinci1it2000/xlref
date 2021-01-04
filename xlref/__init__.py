#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains a comprehensive list of all modules and classes within xlref.

Docstrings should provide sufficient understanding for any individual function.

Modules:

.. currentmodule:: xlref

.. autosummary::
    :nosignatures:
    :toctree: toctree/xlref

    cli
    errors
    filters
    parser
    process
"""
import os
import sys
import functools
from ._version import *

_all = {
    'XlParserError': '.errors',
    'Ref': '.parser',
    'FILTERS': '.filters',
    'dsp': '.process'
}

__all__ = tuple(_all)


@functools.lru_cache(None)
def __dir__():
    return __all__ + (
        '__doc__', '__author__', '__updated__', '__title__', '__version__',
        '__license__', '__copyright__'
    )


def __getattr__(name):
    if name in _all:
        import importlib
        obj = getattr(importlib.import_module(_all[name], __name__), name)
        globals()[name] = obj
        return obj
    raise AttributeError("module %s has no attribute %s" % (__name__, name))


if sys.version_info[:2] < (3, 7) or os.environ.get('IMPORT_ALL') == 'True':
    from .parser import Ref
    from .filters import FILTERS
    from .errors import XlParserError
    from .process import dsp
