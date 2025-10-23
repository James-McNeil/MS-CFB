import struct
import uuid
from datetime import datetime, timezone
from typing import TypeVar


class Filetime:
    """A simple implementation of Windows FILETIME for OLE directory timestamps"""

    def __init__(
        self,
        year: int = 1601,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ):
        if (
            year == 1601
            and month == 1
            and day == 1
            and hour == 0
            and minute == 0
            and second == 0
        ):
            # Default null timestamp
            self._datetime = datetime(1601, 1, 1, tzinfo=timezone.utc)
        else:
            self._datetime = datetime(
                year, month, day, hour, minute, second, tzinfo=timezone.utc
            )

    def to_msfiletime(self) -> int:
        """Convert to Microsoft FILETIME format (100-nanosecond intervals since Jan 1, 1601)"""
        epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
        delta = self._datetime - epoch
        return int(delta.total_seconds() * 10_000_000)

    def __str__(self) -> str:
        return self._datetime.isoformat()


T = TypeVar("T", bound="Directory")


class NullNode:
    """Represents a null node in the red-black tree"""

    def is_null(self) -> bool:
        return True

    def get_flattened_index(self) -> int:
        """Return the flattened index for null nodes (always 0xFFFFFFFF)"""
        return 0xFFFFFFFF


class Directory:
    """An OLE directory object"""

    def __init__(self: T) -> None:
        # The object's name.
        self.name = ""

        # A GUID for this object.
        self._class_id = uuid.UUID(int=0x00)

        # todo:
        self._user_flags = 0

        # Creation and Modification dates.
        self._created = Filetime(1601, 1, 1)
        self._modified = Filetime(1601, 1, 1)

        # The sector where this stream begins
        # This can either be a minifat sector number or a Fat sector
        # depending on the stream size.
        self._start_sector = 0

        # The directory type.
        # probably can be removed.
        self._type = 0

        # This object's index in the flattened representation of the tree.
        self._flattened_index = 0

        # Add color property for red-black tree
        self._color = "black"  # Default to black

        # Red-black tree structure
        self.left = NullNode()
        self.right = NullNode()

        self.prev_index: int
        self.next_index: int
        self.sub_index: int

    def __str__(self: T) -> str:
        return (
            self.get_name()
            + "\n\tCreated: "
            + str(self._created)
            + "\n\tModified: "
            + str(self._modified)
            + "\n\tGUID: "
            + str(self._class_id)
            + "\n\tStart Sector: "
            + str(self.get_start_sector())
            + "\n\tSize: "
            + str(self.file_size())
        )

    @property
    def key(self: T) -> tuple:
        return (len(self.name), self.name.upper())

    @key.setter
    def key(self: T, value: None = None) -> None:
        pass

    def set_created(self: T, value: Filetime) -> None:
        self._created = value

    def get_created(self: T) -> Filetime:
        return self._created

    def set_modified(self: T, value: Filetime) -> None:
        self._modified = value

    def get_modified(self: T) -> Filetime:
        return self._modified

    def get_type(self: T) -> int:
        return self._type

    def set_start_sector(self: T, value: int) -> None:
        self._start_sector = value

    def get_start_sector(self: T) -> int:
        return self._start_sector

    def set_clsid(self: T, clsid: uuid.UUID) -> None:
        self._class_id = clsid

    def get_clsid(self: T) -> uuid.UUID:
        return self._class_id

    def get_name(self: T) -> str:
        return self.name

    def name_size(self: T) -> int:
        """The byte length of the name"""
        return (len(self.name) + 1) * 2

    def set_additional_sectors(self: T, sector_list: list) -> None:
        self._additional_sectors = sector_list

    def file_size(self: T) -> int:
        return 0

    def set_flattened_index(self: T, index: int) -> None:
        self._flattened_index = index

    def get_flattened_index(self: T) -> int:
        """Get the flattened index of this directory"""
        return self._flattened_index

    def get_subdirectory_index(self: T) -> int:
        """
        The the root node of the red-black tree which organizes the streams
        within a storage directory.
        """
        return 0xFFFFFFFF

    def get_color(self: T) -> str:
        """Get the red-black tree node color"""
        return getattr(self, "_color", "black")

    def set_color(self: T, color: str) -> None:
        """Set the red-black tree node color"""
        self._color = color

    def is_null(self: T) -> bool:
        """Check if this is a null node"""
        return False

    def to_bytes(
        self: T, color: int = 1, left: int = 0xFFFFFFFF, right: int = 0xFFFFFFFF
    ) -> bytes:
        format = "<64shbb3I16sIQQIII"
        color = 0 if self.get_color() == "red" else 1
        right = 0
        if self.right.is_null():
            right = 0xFFFFFFFF
        else:
            right = self.right.get_flattened_index()
        left = 0
        if self.left.is_null():
            left = 0xFFFFFFFF
        else:
            left = self.left.get_flattened_index()
        dir = struct.pack(
            format,
            self.name.encode("utf_16_le"),
            self.name_size(),
            self._type,
            color,
            left,
            right,
            self.get_subdirectory_index(),
            self._class_id.bytes_le,
            self._user_flags,
            self._created.to_msfiletime(),
            self._modified.to_msfiletime(),
            self.get_start_sector(),
            self.file_size(),
            0,
        )
        return dir
