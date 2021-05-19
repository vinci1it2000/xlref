#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

"""
It provides functions implementations to filter the parsed data.
"""
import numpy as np
import schedula as sh
from .errors import InvalidReference, NoFullCell


class FiltersFactory(dict):
    def __getitem__(self, item):
        try:
            return super(FiltersFactory, self).__getitem__(item)
        except KeyError:
            return lambda p, x, *args, **kw: getattr(x, item)(*args, **kw)


FILTERS = FiltersFactory({
    'T': lambda parent, x: x.T,
    'array': lambda parent, x, *args, **kw: np.asarray(x, *args, **kw),
})


# noinspection PyUnusedLocal
def full(parent, x):
    """
    Remove the empty value from each row of the input array.

    :param parent:
        Parent parser.
    :type parent: xlref.parser.Ref

    :param x:
        Array.
    :type x: list|numpy.array

    :return:
        Filtered array.
    :rtype: list
    """
    from pandas import notnull
    return [list(filter(notnull, r)) for r in x]


FILTERS['full'] = full


def ref(parent, x):
    """
    If the input is a valid reference, returns the captured values otherwise
    the input.

    :param parent:
        Parent parser.
    :type parent: xlref.parser.Ref

    :param x:
        Input value.
    :type x: object

    :return:
        If the input is a valid reference, returns the captured values otherwise
        the input.
    :rtype: object
    """
    try:
        x = parent.__class__(x, parent, parent.cache).values
    except InvalidReference:
        pass
    except NoFullCell as ex:
        x = ex
    return x


FILTERS['ref'] = ref


def recursive(parent, x, dtype=None):
    """
    Parse recursively all values in the array.

    :param parent:
        Parent parser.
    :type parent: xlref.parser.Ref

    :param x:
        Array.
    :type x: list|numpy.array

    :return:
        Parsed array.
    :rtype: numpy.array
    """
    res, shape = [ref(parent, v) for v in np.ravel(x)], np.shape(x)
    return np.reshape(np.asarray(res, dtype=dtype), shape)


FILTERS['recursive'] = recursive


def _kv(it):
    for k, v in it:
        if isinstance(k, dict):
            yield from k.items()
        else:
            yield k, v


def fdict(parent, x, key=None, value=None):
    """
    Convert the input array into a dictionary.

    :param parent:
        Parent parser.
    :type parent: xlref.parser.Ref

    :param x:
        Array.
    :type x: list|numpy.array

    :param key:
        Filter applied to keys.
    :type key: str|list

    :param value:
        Filter applied to values.
    :type value: str|list

    :return:
        Parsed dictionary.
    :rtype: dict
    """
    from pandas import isnull
    from .parser import compile_filters
    x = x.items() if isinstance(x, dict) else x
    it = ((v[0], v[1] if len(v) == 2 else v[1:]) for v in x if not isnull(v[0]))
    key = key and compile_filters(sh.stlp(key), parent) or (lambda k: k)
    value = value and compile_filters(sh.stlp(value), parent) or (lambda v: v)
    return dict(_kv((key(k), value(v)) for k, v in _kv(it)))


FILTERS['dict'] = fdict
