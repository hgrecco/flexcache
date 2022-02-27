.. image:: https://img.shields.io/pypi/v/flexcache.svg
    :target: https://pypi.python.org/pypi/flexcache
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/flexcache.svg
    :target: https://pypi.python.org/pypi/flexcache
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/flexcache.svg
    :target: https://pypi.python.org/pypi/flexcache
    :alt: Python Versions

.. image:: https://github.com/hgrecco/flexcache/workflows/CI/badge.svg
    :target: https://github.com/hgrecco/flexcache/actions?query=workflow%3ACI
    :alt: CI

.. image:: https://github.com/hgrecco/flexcache/workflows/Lint/badge.svg
    :target: https://github.com/hgrecco/flexcache/actions?query=workflow%3ALint
    :alt: LINTER

.. image:: https://coveralls.io/repos/github/hgrecco/flexcache/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/flexcache?branch=master
    :alt: Coverage


flexcache
=========

An robust and extensible package to cache on disk the result of expensive
calculations.

Consider an expensive function `parse` that takes a path and returns a
parsed version:

.. code-block:: python

    >>> content = parse("source.txt")

It would be nice to automatically and persistently cache this result and
this is where flexcache comes in.

First, we create a `DiskCache` object:

.. code-block:: python

    >>> from flexcache import DiskCacheByMTime
    >>> dc = DiskCacheByMTime(cache_folder="/my/cache/folder")

and then is loaded:

.. code-block:: python

    >>> content = dc.load("source.txt", reader=parse)

If this is the first call, as the cached result is not available,
`parse` will be called on `source.txt` and the output will be saved
and returned. The next time, the cached will be loaded and returned.

When the source is changed, the DiskCache detects that the cached
file is older, calls `parse` again storing and returning the new
result.

In certain cases you would rather detect that the file has changed
by hashing the file. Simply use `DiskCacheByHash` instead of
`DiskCacheByMTime`.

Cached files are saved using the pickle protocol, and each has
a companion json file with the header content.

Building your own caching logic
-------------------------------

In certain cases you would like to customize how caching and
invalidation is done. You can achieve this by subclassing the
`DiskCache`.

.. code-block:: python

    >>> from flexcache import DiskCache
    >>> class MyDiskCache(DiskCache):
    ...
    ...    @dataclass(frozen=True)
    ...    class MyHeader(NameByPathHeader, BasicPythonHeader):
    ...         pass
    ...
    ...    _header_classes = {pathlib.Path: MyHeader}

Here we create a custom Header class and use it to handle `pathlib.Path`
objects. We provide a convenient set of Header classes.

**MinimumHeader**

- source object limitations: None
- header content: source object and identifier of the reader function.
- values used for naming: identifier of the reader function.
- invalidating logic: the cached file exists.

**BasicPythonHeader**: same as MinimumHeader but ...

- source object limitations: None
- header content: source and identifier of the reader function, platform, python implementation, python version.
- values used for naming: identifier of the reader function, platform, python implementation, python version.
- invalidating logic: the cached file exists.

**NameByFileContentHeader**: must be subclassed with MinimumHeader or BasicPythonHeader

- source object limitations:  must be a `pathlib.Path`
- header content: depends on the sibling classes.
- values used for naming: adds file content as bytes.
- invalidating logic: the cached file exists.

**NameByObjHeader**: must be subclassed with MinimumHeader or BasicPythonHeader

- The source object must be pickable.
- header content: depends on the sibling classes. Adds `pickle_protocol`.
- values used for naming: adds pickled object using `pickle_protocol` version.
- invalidating logic: the cached file exists.

**NameByPathHeader**: must be subclassed with MinimumHeader or BasicPythonHeader

- source object limitations: must be a `pathlib.Path`
- header content: depends on the sibling classes.
- values used for naming: adds resolved path.
- invalidating logic: the cached file exists and is newer than the source.

**NameByPathHeader**: must be subclassed with MinimumHeader or BasicPythonHeader

- source object limitations: must be a `pathlib.Path`
- header content: depends on the sibling classes.
- values used for naming: adds resolved paths.
- invalidating logic: the cached file exists and is newer than the newest source.

but you can make your own. Take a look at the code!

----

See AUTHORS_ for a list of the maintainers.

To review an ordered list of notable changes for each version of a project,
see CHANGES_

