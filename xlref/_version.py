# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2020-2021 Vincenzo Arcidiacono;
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

__all__ = ['__version__', '__updated__', '__title__', '__author__',
           '__license__', '__copyright__']

#: Authoritative project's PEP 440 version.
__version__ = version = "1.1.2"  # Also update README.rst

# Please UPDATE TIMESTAMP WHEN BUMPING VERSIONS AND BEFORE RELEASE.
#: Release date.
__updated__ = "2021-05-19 10:35:00"

__title__ = 'xlref'

__author__ = 'Vincenzo Arcidiacono <vinci1it2000@gmail.com>'

__license__ = 'EUPL, see LICENSE.txt'

__copyright__ = 'Copyright 2020-2021 Vincenzo Arcidiacono'

if __name__ == '__main__':
    import sys

    out = ';'.join(
        eval(a[2:].replace('-', '_')) for a in sys.argv[1:] if a[:2] == '--'
    )
    sys.stdout.write(out)
