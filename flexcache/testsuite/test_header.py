import json
import pickle
from dataclasses import asdict as dc_asdict
from dataclasses import dataclass

from flexcache import flexcache


def test_empty(tmp_path):
    hdr = flexcache.MinimumHeader("123", "myreader")
    assert tuple(hdr.for_cache_name()) == ("myreader".encode("utf-8"),)

    p1 = tmp_path / "cache.pickle"
    assert not hdr.is_valid(p1)
    p1.touch()
    assert hdr.is_valid(p1)
    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_basic_python():
    hdr = flexcache.BasicPythonHeader("123", "myreader")
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 4

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_content(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByFileContentHeader, flexcache.MinimumHeader):
        pass

    p = tmp_path / "source.txt"
    p.write_bytes(b"1234")
    hdr = Hdr(p, "myreader")

    assert hdr.source_path == p
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert cn[1] == b"1234"

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_path(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByPathHeader, flexcache.MinimumHeader):
        pass

    p = tmp_path / "source.txt"
    p.write_bytes(b"1234")
    hdr = Hdr(p, "myreader")

    assert hdr.source_path == p
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert cn[1] == bytes(p.resolve())

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_paths(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByMultiplePathsHeader, flexcache.MinimumHeader):
        pass

    p1 = tmp_path / "source1.txt"
    p2 = tmp_path / "source2.txt"
    p1.write_bytes(b"1234")
    p2.write_bytes(b"1234")
    hdr = Hdr((p1, p2), "myreader")

    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 3
    assert cn[1] == bytes(p1.resolve())
    assert cn[2] == bytes(p2.resolve())

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_obj(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByObjHeader, flexcache.MinimumHeader):
        pass

    hdr = Hdr((1, 2, 3), "myreader")

    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert hdr.pickle_protocol == pickle.HIGHEST_PROTOCOL
    assert cn[1] == pickle.dumps((1, 2, 3), hdr.pickle_protocol)

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False
