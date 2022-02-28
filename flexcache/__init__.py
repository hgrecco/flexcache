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
    BaseHeader,
    BasicPythonHeader,
    DiskCache,
    DiskCacheByHash,
    DiskCacheByMTime,
    InvalidateByExist,
    InvalidateByMultiPathsMtime,
    InvalidateByPathMTime,
    NameByFields,
    NameByFileContent,
    NameByHashIter,
    NameByMultiPaths,
    NameByObj,
    NameByPath,
)

__all__ = (
    __version__,
    BaseHeader,
    BasicPythonHeader,
    NameByFields,
    NameByFileContent,
    NameByObj,
    NameByPath,
    NameByMultiPaths,
    NameByHashIter,
    DiskCache,
    DiskCacheByHash,
    DiskCacheByMTime,
    InvalidateByExist,
    InvalidateByPathMTime,
    InvalidateByMultiPathsMtime,
)
