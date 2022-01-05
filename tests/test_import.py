#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2022 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import os
import sys
import unittest
import importlib


@unittest.skipIf(
    sys.version_info[:2] < (3, 7),
    'Not for python version %s.' % '.'.join(map(str, sys.version_info[:3]))
)
class TestImport(unittest.TestCase):
    def setUp(self):
        import xlref as mdl
        self.mdl = mdl

    def reload(self):
        for k in self.mdl.__all__:
            self.mdl.__dict__.pop(k, None)
        return importlib.reload(self.mdl)

    def test_import(self):
        os.environ['IMPORT_ALL'] = 'True'
        mdl = self.reload()
        self.assertTrue(set(mdl.__all__).issubset(mdl.__dict__))
        os.environ['IMPORT_ALL'] = 'False'
        mdl = self.reload()
        self.assertTrue(set(mdl.__all__).isdisjoint(mdl.__dict__))

        with self.assertRaises(AttributeError):
            getattr(mdl, 'ciao')

    def test_dir(self):
        self.assertEqual(dir(self.mdl), [
            'FILTERS', 'Ref', 'XlParserError', '__author__', '__copyright__',
            '__doc__', '__license__', '__title__', '__updated__', '__version__',
            'dsp'
        ])
