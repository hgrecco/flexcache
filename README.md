[![Latest Version](https://img.shields.io/pypi/v/flexcache.svg)](https://pypi.python.org/pypi/flexcache)
[![License](https://img.shields.io/pypi/l/flexcache.svg)](https://pypi.python.org/pypi/flexcache)
[![Python Versions](https://img.shields.io/pypi/pyversions/flexcache.svg)](https://pypi.python.org/pypi/flexcache)
[![CI](https://github.com/hgrecco/flexcache/workflows/CI/badge.svg)](https://github.com/hgrecco/flexcache/actions?query=workflow%3ACI)
[![Coverage](https://coveralls.io/repos/github/hgrecco/flexcache/badge.svg?branch=main)](https://coveralls.io/github/hgrecco/flexcache?branch=main)

# flexcache

A robust and extensible package to cache on disk the result of expensive calculations.

Consider an expensive function `parse` that takes a path and returns a parsed version:

```python
>>> content = parse("source.txt")
```

It would be nice to automatically and persistently cache this result, and this is where flexcache comes in.

First, we create a `DiskCache` object:

```python
>>> from flexcache import DiskCacheByMTime
>>> dc = DiskCacheByMTime(cache_folder="/my/cache/folder")
```

and then load it:

```python
>>> content, basename = dc.load("source.txt", converter=parse)
```

If this is the first call, as the cached result is not available, `parse` will be called on `source.txt`, and the output will be saved and returned. The next time, the cached version will be loaded and returned.

When the source is changed, the DiskCache detects that the cached file is older, calls `parse` again, stores, and returns the new result.

In certain cases, you might prefer detecting that the file has changed by hashing the file. Simply use `DiskCacheByHash` instead of `DiskCacheByMTime`.

Cached files are saved using the pickle protocol, and each has a companion JSON file with the header content.

This idea is completely flexible and applies not only to parsers. In **flexcache**, we say there are two types of objects: **source object** and **converted object**. The conversion function maps the former to the latter, and the cache stores the latter by looking at a customizable aspect of the former.

## Building your own caching logic

In certain cases, you may want to customize how caching and invalidation are done.

You can achieve this by subclassing the `DiskCache`.

```python
>>> from flexcache import DiskCache
>>> class MyDiskCache(DiskCache):
...
...    @dataclass(frozen=True)
...    class MyHeader(NameByPathHeader, InvalidateByExist, BasicPythonHeader):
...         pass
...
...    _header_classes = {pathlib.Path: MyHeader}
```

Here we created a custom Header class and used it to handle `pathlib.Path` objects. You can even have multiple headers registered in the same class to handle different source object types.

We provide a convenient set of mixable classes to achieve almost any behavior. These are divided into three categories, and you must choose at least one from each kind.

### Headers

These classes store the information that will be saved alongside the cached file.

- **BaseHeader**: source object and identifier of the converter function.
- **BasicPythonHeader**: source and identifier of the converter function, platform, Python implementation, and Python version.

### Invalidate

These classes define how the cache will decide if the cached converted object is an actual representation of the source object.

- **InvalidateByExist**: the cached file must exist.
- **InvalidateByPathMTime**: the cached file exists and is newer than the source object (which has to be `pathlib.Path`).
- **InvalidateByMultiPathsMtime**: the cached file exists and is newer than each path in the source object (which has to be `tuple[pathlib.Path]`).

### Naming

These classes define how the name is generated. The basename for the cache file is a hash hexdigest built by feeding a collection of values determined by the Header object.

- **NameByFields**: all fields except the `source_object`.
- **NameByPath**: resolved path of the source object (which has to be `pathlib.Path`).
- **NameByMultiPaths**: resolved path of each path in the source object (which has to be `tuple[pathlib.Path]`), sorted in ascending order.
- **NameByFileContent**: the byte content of the file referred to by the source object (which has to be `pathlib.Path`).
- **NameByHashIter**: the values in the source object (which has to be `tuple[str]`), sorted in ascending order.
- **NameByObj**: the pickled version of the source object (which has to be pickable), using the highest available protocol. This also adds `pickle_protocol` to the header.

You can mix and match as you see fit, and of course, you can create your own.

Finally, you can also avoid saving the header by setting the `_store_header` class attribute to `False`.

______________________________________________________________________

This project was started as part of [Pint](https://github.com/hgrecco/pint), the Python units package.

See [AUTHORS](https://github.com/hgrecco/flexcache/blob/main/AUTHORS) for a list of maintainers.

To review an ordered list of notable changes for each version, see [CHANGES](https://github.com/hgrecco/flexcache/blob/main/CHANGES).
