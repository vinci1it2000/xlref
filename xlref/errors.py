#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

"""
Defines the xlref exceptions.
"""

class XlParserError(Exception):
    msg = None

    def __init__(self, *args):
        if self.msg is not None:
            args = (self.msg,) + args
        super(XlParserError, self).__init__(*args)


class InvalidReference(XlParserError):
    msg = "Invalid xl-ref({}) due to: {}"


class InvalidSyntax(InvalidReference):
    msg = 'Invalid Reference Syntax!'


class NoFullCell(XlParserError):
    msg = 'Full Cell cannot be found form {} with movement {}!'
