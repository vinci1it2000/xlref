Changelog
=========

v1.2.4 (2024-02-27)
-------------------

Fix
~~~
- (parser): Correct engines.


v1.2.3 (2024-02-22)
-------------------

Fix
~~~
- (parser): Update default reader engine and add macro files.

- (doc): Correct issues links.

- (setup): Correct setup config file.


v1.2.2 (2023-11-15)
-------------------

Feat
~~~~
- (setup): Add missing dependencies.

- (bin): Update publish script.

- (doc): Update copyright.

- (test): Use `unittest` for testing instead `nose`.

- (core): Add support for python 3.10 and 3.11.

- (doc): Add Read the Docs configuration file.


Fix
~~~
- (parser): Avoid leaving open file.

- (doc): Remove broken badge.


v1.2.1 (2022-05-10)
-------------------

Feat
~~~~
- (parser): Add open method to open files with custom modules.

- (parser): Add method to read csv files.


Fix
~~~
- (tests): Correct test cases.

- (parser): Correct bug when empty table.

- (filters): Remove warning.


v1.2.0 (2022-01-05)
-------------------

Feat
~~~~
- (doc): Update copyright.

- (actions): Replace travis with github actions.

- (test): Add new test cases.

- (cli): Use `simplejson` to dump parsed data.


Fix
~~~
- (parser): Correct range expansion when is empty.


v1.1.2 (2021-05-19)
-------------------

Feat
~~~~
- (core): Update build scripts.


Fix
~~~
- (parser): Correct file regex.

- (filter): Correct VisibleDeprecationWarning.

- (doc): Correct readme version.


v1.1.1 (2021-01-04)
-------------------

Fix
~~~
- (doc): Update copyrights.

- (parser): Use `openpyxl` to read excel files instead `xlrd`.


v1.1.0 (2020-11-05)
-------------------

Feat
~~~~
- (filters): Remove `merge` option in `dict` filter and add list filters
  for `key` and `value` options.


Fix
~~~
- (travis): Correct coverage setting.


v1.0.1 (2020-11-04)
-------------------

Feat
~~~~
- (filters): Add `merge` option in `dict` filter.


Fix
~~~
- (parser): Implement case insensitive parser for sheet names.


v1.0.0 (2020-04-07)
-------------------
First release.