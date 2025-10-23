import pytest
from ms_cfb.Models.Directories.root_directory import RootDirectory
from ms_dtyp.filetime import Filetime


def test_directory() -> None:

    root_dir = RootDirectory()
    root_dir.name = "Root Entry"
    assert root_dir.name_size() == 22
    ft = Filetime.from_msfiletime(0x01D92433C2B823C0)
    root_dir.set_modified(ft)
    root_dir.set_start_sector(3)
    root_dir.set_color("red")

    ex = [
        "5200 6F00 6F00 7400 2000 4500 6E00 7400",
        "7200 7900 0000 0000 0000 0000 0000 0000",
        "0000 0000 0000 0000 0000 0000 0000 0000",
        "0000 0000 0000 0000 0000 0000 0000 0000",
        "1600 0501 FFFF FFFF FFFF FFFF ffff ffff",
        "0000 0000 0000 0000 0000 0000 0000 0000",
        "0000 0000 0000 0000 0000 0000 C023 B8C2",
        "3324 D901 0300 0000 0000 0000 0000 0000",
    ]

    assert root_dir.to_bytes() == bytes.fromhex(" ".join(ex))


def test_add_created() -> None:
    root_dir = RootDirectory()
    with pytest.raises(Exception):
        date = 0x12345
        root_dir.set_created(date)
