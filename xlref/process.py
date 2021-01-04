#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Defines the file processing chain model `dsp`.
"""
import os
import os.path as osp
import schedula as sh
import collections

#: Process Model.
dsp = sh.BlueDispatcher(name='Processing Model', raises=True)
dsp.add_data('input_references', (), 2)
dsp.add_data('input_fpaths', (), 2)

_FileRefs = collections.namedtuple('_FileRefs', ('obj', 'fpath'))


@sh.add_function(dsp, outputs=['file_references'])
def load_json(input_fpaths):
    """
    Load the data excel references from files.

    :param input_fpaths:
        File paths of the json data excel references.
    :type input_fpaths: list[str]

    :return:
        Data excel references from files.
    :rtype: tuple
    """
    import json
    res = []
    for input_fpath in input_fpaths:
        with open(input_fpath) as f:
            res.append(_FileRefs(json.load(f), input_fpath))
    return res


@sh.add_function(dsp, inputs_kwargs=True, outputs=['references'])
def merge_references(input_references=(), file_references=()):
    """
    Merge data excel references.

    :param input_references:
        Data excel references from user.
    :type input_references: tuple

    :param file_references:
        Data excel references from files.
    :type file_references: tuple

    :return:
        Full list of data excel references.
    :rtype: list
    """
    return list(input_references) + list(file_references)


def _read(references, curr_dir, eskip, pclass, cache):
    if isinstance(references, list):
        return [_read(v, curr_dir, eskip, pclass, cache) for v in references]
    elif isinstance(references, dict):
        args = curr_dir, eskip, pclass, cache
        return {_read(k, *args): _read(v, *args) for k, v in references.items()}
    try:
        p = pclass(references, cache=cache)
        p._curr_dir = curr_dir
        return p.values
    except eskip:
        return references


@sh.add_function(dsp, outputs=['data'])
def read_references(references):
    """
    Read recursively the list of data excel references.

    :param references:
        Full list of data excel references.
    :type references: list

    :return:
        Data output.
    :rtype: list
    """
    from .parser import Ref
    from .errors import InvalidReference
    it = (
        isinstance(r, _FileRefs) and (r.obj, osp.dirname(r.fpath)) or (r, '.')
        for r in references
    )
    args = InvalidReference, Ref, {}
    return [_read(r, d, *args) for r, d in it]


def _json_default(o):
    import numpy as np
    if isinstance(o, np.ndarray):
        return o.tolist()


@sh.add_function(dsp, outputs=['written'])
def save_json(output_fpath, data):
    """
    Save data output in an JSON file.

    :param output_fpath:
        Output file path.
    :type output_fpath: str

    :param data:
        Data output.
    :type data: list

    :return:
        File path where output are written.
    :rtype: str
    """
    import json
    os.makedirs(osp.dirname(output_fpath) or '.', exist_ok=True)
    with open(output_fpath, 'w') as file:
        json.dump(data, file, default=_json_default)
    return output_fpath
