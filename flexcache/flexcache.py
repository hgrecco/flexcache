"""
    flexcache.flexcache
    ~~~~~~~~~~~~~~~~~~~

    Class for persistent caching and invalidating source objects.

    Header
    ------
    Contains summary information about the source object that will
    be saved together with the cached file.

    Members are used:
    - to build the cached filename (see `for_cache_name`)
    - decide whether a given cache file is valid. (see `is_valid`)
    Override these functions to change the logic.

    DiskCache
    ---------
    Saves and loads cached versions of a source object.

    :copyright: 2022 by flexcache Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import abc
import hashlib
import json
import pathlib
import pickle
import platform
import typing
from dataclasses import asdict as dc_asdict
from dataclasses import dataclass
from dataclasses import fields as dc_fields
from typing import Any, Iterable

#########
# Header
#########


@dataclass(frozen=True)
class BaseHeader(abc.ABC):
    """Header with no information.

    The cached file is valid if exists.
    """

    source: Any
    reader_id: str

    def for_cache_name(self) -> typing.Generator[bytes]:
        for el in self._for_cache_name():
            if isinstance(el, str):
                yield el.encode("utf-8")
            else:
                yield el

    def _for_cache_name(self) -> typing.Generator[bytes | str]:
        yield self.reader_id

    @abc.abstractmethod
    def is_valid(self, cache_path: pathlib.Path) -> bool:
        ...


@dataclass(frozen=True)
class BasicPythonHeader(BaseHeader):
    """Header with basic Python information."""

    system: str = platform.system()
    python_implementation: str = platform.python_implementation()
    python_version: str = platform.python_version()


###############
# Naming logic
###############


class NameByFields:
    def _for_cache_name(self):
        yield from super()._for_cache_name()
        for field in dc_fields(self):
            if field.name not in ("source", "reader_id"):
                yield getattr(self, field.name)


class NameByFileContent:
    """Given a file source object, the name is built from its content."""

    @property
    def source_path(self) -> pathlib.Path:
        return self.source

    def _for_cache_name(self):
        yield from super()._for_cache_name()
        yield self.source_path.read_bytes()

    @classmethod
    def from_string(cls, s: str, reader_id: str):
        return cls(pathlib.Path(s), reader_id)


class NameByObj:
    """Given a pickable source object, the name is built from its content."""

    pickle_protocol: int = pickle.HIGHEST_PROTOCOL

    def _for_cache_name(self):
        yield from super()._for_cache_name()
        yield pickle.dumps(self.source, protocol=self.pickle_protocol)


class NameByPath:
    """Given a file source object, the name is built from its resolved path.

    The cached file is valid if exists and is newer than the source file.
    """

    @property
    def source_path(self) -> pathlib.Path:
        return self.source

    def _for_cache_name(self):
        yield from super()._for_cache_name()
        yield bytes(self.source_path.resolve())

    @classmethod
    def from_string(cls, s: str, reader_id: str):
        return cls(pathlib.Path(s), reader_id)


class NameByMultiPaths:
    """Given multiple file source object, the name is built from their resolved path.

    The cached file is valid if exists and is newer than the newest source file.
    """

    @property
    def source_paths(self) -> tuple[pathlib.Path]:
        return self.source

    def _for_cache_name(self):
        yield from super()._for_cache_name()
        yield from sorted(bytes(p.resolve()) for p in self.source_paths)

    @classmethod
    def from_strings(cls, ss: Iterable[str], reader_id: str):
        return cls(tuple(pathlib.Path(s) for s in ss), reader_id)


class NameByHashIter:
    def _for_cache_name(self):
        yield from super()._for_cache_name()
        yield from sorted(h for h in self.source)


#####################
# Invalidation logic
#####################


class InvalidateByExist:
    def is_valid(self, cache_path: pathlib.Path) -> bool:
        return cache_path.exists()


class InvalidateByPathMTime:
    def is_valid(self, cache_path: pathlib.Path):
        return (
            cache_path.exists()
            and cache_path.stat().st_mtime > self.source_path.stat().st_mtime
        )


class InvalidateByMultiPathsMtime:
    @property
    def newest_date(self):
        return max((t.stat().st_mtime for t in self.source_paths), default=0)

    def is_valid(self, cache_path: pathlib.Path):
        return cache_path.exists() and cache_path.stat().st_mtime > self.newest_date


class DiskCache:
    """

    Parameters
    ----------
    cache_folder
        indicates where the cache files will be saved.
    """

    # Maps classes
    _header_classes: dict[type, BaseHeader] = None

    # Hasher object constructor (e.g. a member of hashlib)
    # must implement update(b: bytes) and hexdigest() methods
    _hasher = hashlib.sha1

    # If True, for each cached file the header is also stored.
    _store_header: bool = True

    def __init__(self, cache_folder: str | pathlib.Path):
        self.cache_folder = pathlib.Path(cache_folder)
        self.cache_folder.mkdir(parents=True, exist_ok=True)
        self._header_classes = self._header_classes or {}

    def register_header_class(self, object_class: type, header_class: BaseHeader):
        self._header_classes[object_class] = header_class

    def cache_stem_for(self, header: BaseHeader) -> str:
        """Generate a hash representing the location of a memoized file
        for a given filepath or object.
        """
        hd = self._hasher()
        for value in header.for_cache_name():
            hd.update(value)
        return hd.hexdigest()

    def cache_path_for(self, header: BaseHeader) -> pathlib.Path:
        """Generate a Path representing the location of a memoized file
        for a given filepath or object.
        """
        h = self.cache_stem_for(header)
        return self.cache_folder.joinpath(h).with_suffix(".pickle")

    def _get_header_class(self, source_object) -> BaseHeader:
        for k, v in self._header_classes.items():
            if isinstance(source_object, k):
                return v
        raise TypeError(f"Cannot find header class for {type(source_object)}")

    def load(self, source_object, reader=None, pass_hash=False) -> tuple[Any, str]:
        """Load and return the cached file if exists, and it's hash
        differ from the actual
        """
        header_class = self._get_header_class(source_object)
        reader_id = reader.__name__ if reader is not None else ""
        header = header_class(source_object, reader_id)

        cache_path = self.cache_path_for(header)

        content = self.rawload(header, cache_path)

        if content:
            return content, cache_path.stem
        if reader is None:
            return None, cache_path.stem

        if pass_hash:
            content = reader(source_object, cache_path.stem)
        else:
            content = reader(source_object)

        self.rawsave(header, content, cache_path)

        return content, cache_path.stem

    def save(self, obj, source_object) -> str:
        """Save the object (in pickle format) to the cache folder
        using a unique name generated using `cache_path_for`
        """
        header_class = self._get_header_class(source_object)
        header = header_class(source_object, "")
        return self.rawsave(header, obj, self.cache_path_for(header)).stem

    def rawload(
        self, header: BaseHeader, cache_path: pathlib.Path = None
    ) -> Any | None:
        if cache_path is None:
            cache_path = self.cache_path_for(header)

        if header.is_valid(cache_path):
            with cache_path.open(mode="rb") as fi:
                return pickle.load(fi)

    def rawsave(
        self, header: BaseHeader, obj, cache_path: pathlib.Path = None
    ) -> pathlib.Path:
        """Save the object (in pickle format) to the cache folder
        using a unique name generated using `cache_path_for`
        """
        if cache_path is None:
            cache_path = self.cache_path_for(header)

        if self._store_header:
            with cache_path.with_suffix(".json").open("w", encoding="utf-8") as fo:
                json.dump({k: str(v) for k, v in dc_asdict(header).items()}, fo)
        with cache_path.open(mode="wb") as fo:
            pickle.dump(obj, fo)
        return cache_path


class DiskCacheByHash(DiskCache):
    @dataclass(frozen=True)
    class Header(InvalidateByExist, NameByFileContent, BaseHeader):
        pass

    _header_classes = {
        pathlib.Path: Header,
        str: Header.from_string,
    }


class DiskCacheByMTime(DiskCache):
    @dataclass(frozen=True)
    class Header(InvalidateByPathMTime, NameByPath, BaseHeader):
        pass

    _header_classes = {
        pathlib.Path: Header,
        str: Header.from_string,
    }
