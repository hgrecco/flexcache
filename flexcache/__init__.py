"""
    flexcache
    ~~~~~~~~~

    Classes for persistent caching and invalidating source objects.

    :copyright: 2022 by flexcache Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


import pkg_resources

try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("flexcache").version
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"

from .flexcache import (
    BasicPythonHeader,
    DiskCache,
    DiskCacheByHash,
    DiskCacheByMTime,
    MinimumHeader,
    NameByFileContentHeader,
    NameByMultiplePathsHeader,
    NameByObjHeader,
    NameByPathHeader,
)

__all__ = (
    __version__,
    MinimumHeader,
    BasicPythonHeader,
    NameByFileContentHeader,
    NameByObjHeader,
    NameByPathHeader,
    NameByMultiplePathsHeader,
    DiskCache,
    DiskCacheByHash,
    DiskCacheByMTime,
)
