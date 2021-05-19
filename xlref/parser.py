#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It provides xlparser reference parser class.
"""
import re
import string
import logging
import numpy as np
import os.path as osp
from .filters import FILTERS
from .errors import InvalidSyntax, InvalidReference, NoFullCell

log = logging.getLogger(__name__)

_primitive_dir = dict(zip(
    'LURD', np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], int)
))

# noinspection RegExpRedundantEscape
_re_xl_ref_parser = re.compile(
    r"""
    ^\s*(?:(?P<file>[^!#]+)?)?\s*\#\s*                      # xl file name
    (?:(?P<sheet>[^!]+)?!)?\s*                              # xl sheet name
    (?:                                                     # first cell
        (?P<st_col>[A-Z]+|_|\^)\s*                          # first col
        (?P<st_row>\d+|_|\^)\s*                             # first row
        (?:\(\s*
            (?P<st_mov>L|U|R|D|LD|LU|UL|UR|RU|RD|DL|DR)\s*  # moves from st cell
            \)
        )?
    )\s*
    (?::\s*                                                 # second cell [opt]
        (?P<nd_col>[A-Z]+|_|\^|\.)\s*                       # second col
        (?P<nd_row>\d+|_|\^|\.)\s*                          # second row
        (?:\(\s*
            (?P<nd_mov>L|U|R|D|LD|LU|UL|UR|RU|RD|DL|DR)\s*  # moves from nd cell
            \)
        )?
    )?\s*
    (?::\s*
            (?P<range_exp>[LURD]+)                          # expansion [opt]
    )?\s*
    (?:
        \s*(?P<filters>[\[{].*[\]}])\s*                     # filters [opt]
    )?\s*$""", re.IGNORECASE | re.X)


def _row2num(coord):
    if coord in '^_.':
        return coord
    return int(coord) - 1


def _col2num(coord):
    if coord in '^_.':
        return coord
    num = 0
    for c in coord.upper():
        num = num * 26 + string.ascii_uppercase.rindex(c) + 1
    return num - 1


def _num2col(num):
    d = num // 26
    chr1 = _num2col(d) if d > 0 else ''
    return '%s%s' % (chr1, chr(ord('A') + num % 26))


class Range:
    def __init__(self, st_cell, nd_cell):
        (self.r0, self.c0), (self.r1, self.c1) = st_cell, nd_cell

    def get(self):
        return self.r0, self.c0, self.r1, self.c1

    def __repr__(self):
        return '%s%d:%s%d' % (
            _num2col(self.c0), self.r0 + 1, _num2col(self.c1), self.r1 + 1
        )


# noinspection PyTypeChecker
class Ref:
    """Reference parser"""
    _curr_dir = '.'
    _engines = {
        'xlsx': 'openpyxl',
        'xls': 'xlrd',
        'odf': 'odf',
        'ods': 'odf',
        'odt': 'odf',
        None: 'pyxlsb'
    }
    _re = _re_xl_ref_parser
    _open_sheet_kw = {'header': None}

    def _match(self, ref):
        m = self._re.match(ref)
        if not m:
            raise InvalidSyntax(ref)
        return m.groupdict()

    def __init__(self, ref, parent=None, cache=None):
        try:
            d = self._match(ref)
            p = d.pop
            d['st_ref'] = self._ref(p('st_col'), p('st_row'), p('st_mov'))
            d['nd_ref'] = self._ref(p('nd_col'), p('nd_row'), p('nd_mov'))
            d['filters'] = self._parse_filters(d['filters'] or '[]')
            self.ref = d
            self.parent = parent
            self.cache = {} if cache is None else cache
        except InvalidSyntax as ex:
            raise ex
        except Exception as ex:
            raise InvalidReference(ref, ex)

    @staticmethod
    def _parse_filters(s):
        from json import loads
        v = loads(s)
        return [v] if isinstance(v, dict) else v

    @staticmethod
    def _ref(cell_col, cell_row, cell_mov):
        if cell_col == cell_row == cell_mov is None:
            return None
        row = _row2num(cell_row)
        col = _col2num(cell_col)
        mov = cell_mov.upper() if cell_mov else None
        return (row, col), mov

    def _open_workbook(self, fpath):
        from pandas import ExcelFile
        ext = osp.splitext(fpath.lower())[1][1:]
        engine = self._engines.get(ext, self._engines[None])
        wb = ExcelFile(fpath, engine=engine)
        wb.sheet_indices = {k.lower(): i for i, k in enumerate(wb.sheet_names)}
        return wb

    def _open_sheet(self, workbook, name):
        name = getattr(workbook, 'sheet_indices', {}).get(name, name)
        return workbook.parse(name, **self._open_sheet_kw).values

    @property
    def book(self):
        if 'xl_book' not in self.ref:
            fp = self.ref['file']
            if fp:
                curr_dir = self._curr_dir
                if self.parent:
                    curr_dir = osp.dirname(self.parent.ref['fpath'])
                self.ref['fpath'] = fp = osp.abspath(osp.join(curr_dir, fp))
                if fp in self.cache:
                    wb = self.cache[fp]
                else:
                    self.cache[fp] = wb = self._open_workbook(fp)
            else:
                self.ref['fpath'] = self.parent.ref.get('fpath')
                wb = self.parent.book
            self.ref['xl_book'] = wb
        return self.ref['xl_book']

    @property
    def sheet(self):
        if 'xl_sheet' not in self.ref:
            sn = self.ref['sheet']
            if sn:
                wb, sn = self.book, sn.lower()
                if (wb, sn) in self.cache:
                    sheet = self.cache[(wb, sn)]
                else:
                    self.cache[(wb, sn)] = sheet = self._open_sheet(wb, sn)
            else:
                sheet = self.parent.sheet
            self.ref['xl_sheet'] = sheet
        return self.ref['xl_sheet']

    @property
    def full_cells(self):
        if 'full_cells' not in self.ref:
            from pandas import isnull
            self.ref['full_cells'] = ~isnull(self.sheet)
        return self.ref['full_cells']

    @property
    def margins(self):
        if 'margins' not in self.ref:
            indices = np.array(np.where(self.full_cells)).T
            up_r, up_c = indices.min(0)
            dn_r, dn_c = indices.max(0)
            m = {'^': up_r, '_': dn_r}, {'^': up_c, '_': dn_c}
            self.ref['margins'] = m
        return self.ref['margins']

    def _target_full(self, cell, moves):
        up, dn = (0, 0), (self.margins[0]['_'], self.margins[1]['_'])
        mv = _primitive_dir[moves[0]]  # first move
        c0, full_cells = np.array(cell), self.full_cells

        if 'U' in moves and not c0[0] <= dn[0]:
            c0[0] = dn[0]
        if 'L' in moves and not c0[1] <= dn[1]:
            c0[1] = dn[1]

        while (up <= c0).all() and (c0 <= dn).all():
            c1 = c0.copy()
            while (up <= c1).all():
                try:
                    if full_cells[c1[0], c1[1]]:
                        return c1
                except IndexError:
                    break
                c1 += mv
            try:
                c0 += _primitive_dir[moves[1]]  # second move
            except IndexError:
                break
        raise NoFullCell(cell, moves)

    def _resolve_ref(self, ref, pcell=None):
        row, col = ref[0]
        if row in ('^', '_'):
            row = self.margins[0][row]
        elif row == '.':
            row = pcell[0]
        if col in ('^', '_'):
            col = self.margins[1][col]
        elif col == '.':
            col = pcell[1]
        try:
            state = self.full_cells[row, col]
        except IndexError:
            state = False
        if not (state or ref[1] is None):
            row, col = self._target_full((row, col), ref[1])
        return row, col

    def _expand_range(self, st, nd, range_exp):
        range_exp, exp = range_exp.upper(), np.zeros((2, 2), int)
        for k, i in (('L', 0), ('U', 0), ('R', 1), ('D', 1)):
            exp[:, i] += _primitive_dir[k] * range_exp.count(k)
        # noinspection PyUnresolvedReferences
        empty, rng = ~self.full_cells, np.array((st, nd), int).T + [0, 1]
        b = np.array([True])
        margins = np.array([(m['^'], m['_'] + 1) for m in self.margins]).T
        while b.any():
            empty[slice(*rng[0]), slice(*rng[1])] = True
            r = np.clip(rng + exp, margins[0, :, None], margins[1, :, None])
            b = ~np.array([
                empty[r[0] - [0, 1], slice(*r[1])].all(1),
                empty[slice(*r[0]), r[1] - [0, 1]].all(0)
            ])
            rng = np.where(b, r, rng)
        return list(map(tuple, (rng - [0, 1]).T))

    @property
    def range(self):
        if 'rect' not in self.ref:
            nd = st = self._resolve_ref(self.ref['st_ref'])
            nd_ref, range_exp = self.ref['nd_ref'], self.ref['range_exp']
            if nd_ref is not None:
                nd = self._resolve_ref(nd_ref, st)
                r, c = (st[0], nd[0]), (st[1], nd[1])
                st, nd = (min(r), min(c)), (max(r), max(c))
            if range_exp is not None:
                st, nd = self._expand_range(st, nd, range_exp)
            self.ref['rect'] = Range(st, nd)
        return self.ref['rect']

    @property
    def values(self):
        if 'values' not in self.ref:
            r0, c0, r1, c1 = self.range.get()
            v = self.sheet[r0:r1 + 1, c0:c1 + 1]
            self.ref['values'] = compile_filters(self.ref['filters'], self)(v)
        return self.ref['values']


def compile_filters(filters, parent):
    it = (dict(k) if isinstance(k, dict) else {'fun': k} for k in filters)
    it = [(v.pop('fun'), v.get('args', ()), v.get('kw', v)) for v in it]

    def call_filters(value):
        for k, args, kw in it:
            value = FILTERS[k](parent, value, *args, **kw)
        return value

    return call_filters
