from ms_cfb.Models.Directories.directory import Directory, NullNode
from typing import TypeVar, Iterator


class RedBlackTree:
    """Simple red-black tree implementation for Directory objects"""

    def __init__(self):
        self.root = NullNode()

    def insert(self, node: Directory) -> None:
        """Insert a directory node into the tree"""
        if self.root.is_null():
            self.root = node
            node.set_color("black")
        else:
            self._insert_recursive(self.root, node)

    def _insert_recursive(self, current: Directory, new_node: Directory) -> None:
        """Recursive helper for insertion"""
        if new_node.key < current.key:
            if current.left.is_null():
                current.left = new_node
                new_node.set_color("red")
            else:
                self._insert_recursive(current.left, new_node)
        else:
            if current.right.is_null():
                current.right = new_node
                new_node.set_color("red")
            else:
                self._insert_recursive(current.right, new_node)

    def find(self, key: tuple) -> Directory:
        """Find a node by key"""
        return self._find_recursive(self.root, key)

    def _find_recursive(self, current, key: tuple):
        """Recursive helper for finding nodes"""
        if current.is_null():
            return None
        if key == current.key:
            return current
        elif key < current.key:
            return self._find_recursive(current.left, key)
        else:
            return self._find_recursive(current.right, key)

    def __iter__(self) -> Iterator[Directory]:
        """In-order traversal of the tree"""
        yield from self._inorder(self.root)

    def _inorder(self, node) -> Iterator[Directory]:
        """In-order traversal helper"""
        if not node.is_null():
            yield from self._inorder(node.left)
            yield node
            yield from self._inorder(node.right)


T = TypeVar("T", bound="StorageDirectory")


class StorageDirectory(Directory):
    """
    A StorageDirectory represents a file system directory. It adds a red-black
    tree to the parent class as a way to organize its contents.
    """

    def __init__(self: T, name: str) -> None:
        super(StorageDirectory, self).__init__()
        self.name = name
        self._type = 1
        self.directories = RedBlackTree()

    def __str__(self: T) -> str:
        return (
            self.get_name()
            + "\n\tCreated: "
            + str(self._created)
            + "\n\tModified: "
            + str(self._modified)
            + "\n\tGUID: "
            + str(self._class_id)
        )

    def insert(self: T, node: Directory) -> None:
        self.directories.insert(node)

    def get_subdirectory_index(self: T) -> int:
        """
        Overriding Directory.get_subdirectory_index()
        If the red-black tree has a root, return its flattened index.
        """
        dir = self.directories
        node = dir.root
        if node.is_null():
            return 0xFFFFFFFF
        assert isinstance(node, Directory)
        return node._flattened_index

    def minifat_sectors_used(self: T) -> int:
        size = 0
        for dir in self.directories:
            size += dir.minifat_sectors_used()
        return size

    def add_directory(self: T, dir: "Directory") -> None:
        self.directories.insert(dir)

    def flatten(self: T) -> list:
        flat = [self]
        for child in self.directories:
            if child._type != 2:
                flat.extend(child.flatten())
            else:
                flat.append(child)
        i = 0
        for dir in flat:
            dir._flattened_index = i
            i += 1
        return flat

    def get_tree_data(self: T, dir: Directory) -> tuple[int, int, int]:
        key = dir.key
        node = self.directories.find(key)
        if node is None:
            return (1, 0xFFFFFFFF, 0xFFFFFFFF)

        right_index = (
            0xFFFFFFFF if node.right.is_null() else node.right.get_flattened_index()
        )
        left_index = (
            0xFFFFFFFF if node.left.is_null() else node.left.get_flattened_index()
        )
        color = 0 if node.get_color() == "red" else 1

        return (color, right_index, left_index)

    def create_file_tree(self: T, depth: int) -> list:
        tree = [(depth, self.name)]
        for child in self.directories:
            if child._type != 2:
                tree.extend(child.create_file_tree(depth + 1))
            else:
                tree.append((depth + 1, child.name))
        return tree
