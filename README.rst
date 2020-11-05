.. _start-intro:

##########################
xlref: Excel table reader.
##########################
|pypi_ver| |travis_status| |cover_status| |docs_status| |dependencies|
|github_issues| |python_ver| |proj_license|

:release:       1.1.0
:date:          2020-11-05 23:40:00
:repository:    https://github.com/vinci1it2000/xlref
:pypi-repo:     https://pypi.org/project/xlref/
:docs:          http://xlref.readthedocs.io/
:wiki:          https://github.com/vinci1it2000/xlref/wiki/
:download:      http://github.com/vinci1it2000/xlref/releases/
:donate:        https://donorbox.org/xlref
:keywords:      data, excel, tables, parser, reference, ranges
:developers:    .. include:: AUTHORS.rst
:license:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_

.. _end-intro:
.. _start-about:
.. _start-0-pypi:

About xlref
===========
**xlref** is an useful library to capture by a simple reference (e.g.,
`A1(RD):..:RD`) a table with non-empty cells from Excel-sheets when its exact
position is not known beforehand.

This code was inspired by the `xleash` module of the
`pandalone <https://github.com/pandalone/pandalone>`_ library. The reason of
developing a similar tool was to have a smaller library to install and improve
the performances of reading `.xlsx` files.

.. _end-0-pypi:
.. _end-about:
.. _start-install:

Installation
============
To install it use (with root privileges):

.. code-block:: console

    $ pip install xlref

Or download the last git version and use (with root privileges):

.. code-block:: console

    $ python setup.py install

.. _end-install:
.. _start-syntax:

Reference Syntax
================
The `capturing` is preformed according to an excel like reference syntax and the
non-empty cells of the targeted excel-sheet. The syntax is defined as follows:

 [<excel>]#[<sheet>!]<st-cel>[(<moves>)][:<nd-cel>[(<moves>)]][:<expansion>][<filters>]

.. note:: The fields between square parenthesis are optionals.

Follows the description of the parameters:

    - **excel**: excel file path relative to the parent reference file
      directory. If not defined, the parent reference excel is inherited.
    - **sheet**: excel sheet name if not defined, the parent reference excel
      sheet name is inherited.
    - **st-cel**: first cell coordinate of excel range. The cell coordinate
      (i.e., `<column><row>`) is defined by a column (letter) and row (number),
      like in excel. `xlref` allows two special characters `^` and `_`, that
      represents the leftmost/topmost and rightmost/bottommost non-empty cell
      column/row.
    - **moves**: the sequence of primitive directions (i.e., `L`:left, `U`: up,
      `R`: right, `D`: down) that `xlref` uses iteratively for finding the
      first non-empty cell. The allowed primitive direction combinations are
      `L`, `U`, `R`, `D`, `LD`, `LU`, `UL`, `UR`, `RU`, `RD`, `DL`, and `DR`.
      The following diagram shows the graphically the `moves` from the starting
      cell `X`::

                U
         UL◄───┐▲┌───►UR
        LU     │││     RU
         ▲     │││     ▲
         │     │││     │
         └─────┼│┼─────┘
        L◄──────X──────►R
         ┌─────┼│┼─────┐
         │     │││     │
         ▼     │││     ▼
        LD     │││     RD
         DL◄───┘▼└───►DR
                D

    - **nd-cel**: second cell coordinate of excel range. It has the same syntax
      of the `st-cel`, but it has and extra special character `.`. This
      represents the column or row of the `st-cel` after the application of the
      `moves`.
    - **expansion**: the sequence of primitive directions to expand the captured
      range.
    - **filters**: list of string and or dictionaries that defines the filters
      to apply iteratively on the captured range.

Reference Reading Steps
-----------------------
The library performs the following steps to read a reference:

    1. Open the excel file or inherits the parent's one,
    2. Open the sheet by its name or inherits the parent's one,
    3. Set the first range cell,
    4. Move the first cell according to the specified `moves` until it finds the
       first non-empty cell,
    5. Set the second range cell or inherits the moved first range cell,
    6. Move the second cell like in point `4`,
    7. Expand the range according to the defined `expansions`,
    8. Apply the iteratively the filters on the captured range.

.. _end-syntax:
.. _start-tutorial:
.. _start-1-pypi:

Tutorial
========
.. testsetup::

    >>> import os.path as osp
    >>> from setup import mydir
    >>> _ref = osp.join(mydir, 'tests/files/excel.xlsx#ref!A1(RD):RD[%s]')

A typical example is `capturing` a table with a "header" row and convert into a
dictionary. The code below shows how to do it:

    >>> import xlref as xl
    >>> _ref = 'excel.xlsx#ref!A1(RD):RD[%s]'  # doctest: +SKIP
    >>> ref = xl.Ref(_ref % '"dict"')
    >>> ref.range  # Captured range.
    B2:C25
    >>> values = ref.values; values  # Captured values.
    {...}
    >>> values['st-cell-move']
    '#D5(RU):H1(DL)'

You can notice from the code above that all the values of the dictionary are
references. To parse it recursively, there are two options:

    1. add the "recursive" filter before the "dict":

       >>> values = xl.Ref(_ref % '"recursive", "dict"').values
       >>> values['st-cell-move'].tolist()
       [[1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]]

    2. apply a filter onto dictionary' values using the extra functionality of
       the "dict" filter:

       >>> values = xl.Ref(_ref % '{"fun": "dict", "value":"ref"}').values
       >>> values['st-cell-move'].tolist()
       [[1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]]

You have also the possibility to define and use your custom filters as follows:

    >>> import numpy as np
    >>> xl.FILTERS['my-filter'] = lambda parent, x: np.sum(x)
    >>> xl.Ref('#D5(RU):H1(DL)["my-filter"]', ref).values
    45.0

An alternative way is to use directly the methods of the filtered results as
follows:

    >>> xl.Ref('#D5(RU):H1(DL)["sum"]', ref).values
    45.0

.. _end-tutorial:
.. _end-1-pypi:
.. _start-badges:

.. |travis_status| image:: https://travis-ci.org/vinci1it2000/xlref.svg?branch=master
    :alt: Travis build status
    :target: https://travis-ci.org/vinci1it2000/xlref

.. |cover_status| image:: https://coveralls.io/repos/github/vinci1it2000/xlref/badge.svg?branch=master
    :target: https://coveralls.io/github/vinci1it2000/xlref?branch=master
    :alt: Code coverage

.. |docs_status| image:: https://readthedocs.org/projects/xlref/badge/?version=stable
    :alt: Documentation status
    :target: https://xlref.readthedocs.io/en/stable/?badge=stable

.. |pypi_ver| image::  https://img.shields.io/pypi/v/xlref.svg?
    :target: https://pypi.python.org/pypi/xlref/
    :alt: Latest Version in PyPI

.. |python_ver| image:: https://img.shields.io/pypi/pyversions/xlref.svg?
    :target: https://pypi.python.org/pypi/xlref/
    :alt: Supported Python versions

.. |github_issues| image:: https://img.shields.io/github/issues/vinci1it2000/xlref.svg?
    :target: https://github.com/vinci1it2000/xlref/issues
    :alt: Issues count

.. |proj_license| image:: https://img.shields.io/badge/license-EUPL%201.1%2B-blue.svg?
    :target: https://raw.githubusercontent.com/vinci1it2000/xlref/master/LICENSE.txt
    :alt: Project License

.. |dependencies| image:: https://img.shields.io/requires/github/vinci1it2000/xlref.svg?
    :target: https://requires.io/github/vinci1it2000/xlref/requirements/?branch=master
    :alt: Dependencies up-to-date?

.. _end-badges:
