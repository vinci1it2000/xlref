#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2023 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import os
import ddt
import json
import shutil
import unittest
import os.path as osp
import xlref.cli as cli
from click.testing import CliRunner

test_dir = osp.dirname(__file__)
files_dir = osp.join(test_dir, 'files')
results_dir = osp.join(test_dir, 'results')
files = dict(
    xl=osp.join(test_dir, 'files', 'excel.xlsx'),
    json=osp.join(test_dir, 'files', 'test.json'),
    csv=osp.join(test_dir, 'files', 'test.csv')
)


@ddt.ddt
class TestCMD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = osp.join(test_dir, 'temp')
        cls.runner = CliRunner()
        shutil.rmtree(cls.temp, ignore_errors=True)
        os.makedirs(cls.temp, exist_ok=True)
        os.chdir(cls.temp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp, ignore_errors=True)

    @ddt.idata((
            ([], 2, 0),
            (['out.json', '-v', 'DEBUG'], 0, 1),
            (['out1.json',
              '%s#ReF!B2:C_[{"fun":"dict","key":"lower","value":"ref"}]' %
              files['xl']], 0, 1),
            (['out2.json'] + [
                '%s#origin!A1["recursive"]' % files['xl']
            ] * 2, 0, 1),
            (['out3.json', '%s#origin!A1["recursive"]' % files['xl'], '-F',
              files['json']], 0, 1),
            (['out4.json', '-F', files['json'], '-F', files['json']], 0, 1),
            (['out5.json', '%s#A1:..:DR' % files['csv']], 0, 1),
    ))
    def test_read(self, data):
        args, exit_code, file = data
        self.maxDiff = None
        result = self.runner.invoke(cli.read, args)
        self.assertEqual(exit_code, result.exit_code, result)
        if file:
            self.assertTrue(osp.isfile(args[0]))
            res = osp.join(results_dir, args[0])
            if osp.isfile(res):
                with open(res) as e, open(args[0]) as r:
                    self.assertEqual(json.load(e), json.load(r))


@ddt.ddt
class TestRange(unittest.TestCase):
    def test_range_repr(self):
        from xlref.parser import Range
        self.assertEqual(str(Range((1, 2), (5, 6))), 'C2:G6')
