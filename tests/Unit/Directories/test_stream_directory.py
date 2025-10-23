import pytest
import uuid
from ms_cfb.Models.Directories.stream_directory import StreamDirectory


def test_constructor() -> None:
    stream_dir = StreamDirectory("name", "/path")
    assert isinstance(stream_dir, StreamDirectory)


def test_add_created() -> None:
    stream_dir = StreamDirectory("name", "/path")
    with pytest.raises(Exception):
        date = 0x12345
        stream_dir.set_created(date)


def test_add_modified() -> None:
    stream_dir = StreamDirectory("name", "/path")
    date = 0x12345
    with pytest.raises(Exception):
        stream_dir.set_modified(date)


def test_file_size() -> None:
    stream_dir = StreamDirectory("name", "tests/Test.txt")
    assert stream_dir.file_size() == 5


def test_sectors_used() -> None:
    stream_dir = StreamDirectory("name", "tests/Test.txt")
    assert stream_dir.minifat_sectors_used() == 1


def test_class_id_exception() -> None:
    stream_dir = StreamDirectory("name", "/path")
    guid = uuid.uuid1()
    with pytest.raises(Exception):
        stream_dir.set_clsid(guid)


def test_class_id() -> None:
    stream_dir = StreamDirectory("name", "/path")
    assert stream_dir.get_clsid().int == 0x00
    guid = uuid.UUID(int=0x00)
    stream_dir.set_clsid(guid)
    assert stream_dir.get_clsid().int == 0x00
