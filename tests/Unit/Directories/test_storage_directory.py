from ms_cfb.Models.Directories.storage_directory import StorageDirectory


def test_constructor() -> None:
    storage_dir = StorageDirectory("name")
    assert storage_dir.get_type() == 1
    assert isinstance(storage_dir, StorageDirectory)
