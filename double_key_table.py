from __future__ import annotations

import unittest
from typing import Generic, TypeVar, Iterator

import setuptools.command.alias

from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR
from mountain import Mountain

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')
T = TypeVar('T')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise, `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise, `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241,
                   786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        """
        Creating a 2D array (Table within a Table)
        """
        self.outer_table = LinearProbeTable(sizes)
        self.internal_sizes = internal_sizes

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        position1 = self.hash1(key1)

        for _ in range(self.outer_table.table_size):
            if self.outer_table.array[position1] is None:
                if is_insert:
                    # create the internal hash table if is_insert is true
                    self.outer_table.count += 1
                    self.outer_table.array[position1] = (key1, LinearProbeTable(self.internal_sizes))
                    internal_table = self.outer_table.array[position1][1]

                    # ensures any internal table uses hash2 for hashing keys.
                    internal_table.hash = lambda k: self.hash2(k, internal_table)

                    position2 = internal_table.hash(key2)
                    return position1, position2
                else:
                    raise KeyError(key1)
            elif self.outer_table.array[position1][0] == key1:
                inner_table = self.outer_table.array[position1][1]
                return position1, inner_table._linear_probe(key2, is_insert)
            else:
                position1 = (position1 + 1) % self.outer_table.table_size

        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError(key1)

    def keys(self, key: K1 | None = None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        keys = []
        if key:
            self.outer_table.hash = lambda k: self.hash1(key)
            inner_table = self.outer_table.array[self.outer_table._linear_probe(key, False)][1]
            for item in inner_table.array:
                if item is not None:
                    keys.append(item[0])
        else:
            return self.outer_table.keys()
        return keys

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        values = []
        if key is None:
            keys = self.keys()
            for key in keys:
                self.outer_table.hash = lambda k: self.hash1(key)
                inner_table = self.outer_table.array[self.outer_table._linear_probe(key, False)][1]
                for item in inner_table.array:
                    if item is not None:
                        values.append(item[1])
        else:
            self.outer_table.hash = lambda k: self.hash1(key)
            inner_table = self.outer_table.array[self.outer_table._linear_probe(key, False)][1]
            for item in inner_table.array:
                if item is not None:
                    values.append(item[1])

        return values

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            iterator = HashTableIterator(self.outer_table)
            return iterator
        else:
            inner_index = None
            for i in range(self.outer_table.table_size):
                if self.outer_table.array[i] is not None:
                    if self.outer_table.array[i][0] == key:
                        inner_index = i
                        break
                else:
                    continue
            iterator = HashTableIterator((self.outer_table.array[inner_index][1]))
            return iterator

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        # if key is None:
        #     return iter(self.values())
        # else:
        #     return iter(self.values(key))
        if key is None:
            iterator = HashTableIterator(self.outer_table)
            iterator.values = True
            iterator.outer = True
            return iterator
        else:
            inner_index = None
            for i in range(self.outer_table.table_size):
                if self.outer_table.array[i] is not None:
                    if self.outer_table.array[i][0] == key:
                        inner_index = i
                        break
                else:
                    continue
            iterator = HashTableIterator((self.outer_table.array[inner_index][1]))
            iterator.values = True
            return iterator

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def _getitem_(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        positions = self._linear_probe(key[0], key[1], False)
        return self.outer_table.array[positions[0]][1].array[positions[1]][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set a (key, value) pair in our hash table.
        """
        positions = self._linear_probe(key[0], key[1], True)
        internal_table = self.outer_table.array[positions[0]][1]

        internal_table.array[positions[1]] = (key[1], data)
        internal_table.count += 1

        if len(internal_table) > internal_table.table_size / 2:
            internal_table._rehash()

        if len(self.outer_table) > self.outer_table.table_size / 2:
            self._rehash()

        return

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        positions = self._linear_probe(key[0], key[1], False)
        outer_index = positions[0]
        inner_index = positions[1]
        # The linear probe will raise the key errors if the keys don't exist
        inner_table = self.outer_table.array[outer_index][1]
        inner_table.array[inner_index] = None
        inner_table.count -= 1

        inner_index = (inner_index + 1) % inner_table.table_size
        while inner_table.array[inner_index] is not None:
            key2, value = inner_table.array[inner_index]
            inner_table.array[inner_index] = None
            # Reinsert.
            newpos = self._linear_probe(key[0], key2, True)
            inner_table.array[newpos[1]] = (key2, value)
            inner_index = (inner_index + 1) % self.table_size

        if self.outer_table.array[outer_index][1].count == 0:
            self.outer_table.array[outer_index] = None
            self.outer_table.count -= 1

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        temp_copy = self.outer_table.array

        self.outer_table.size_index += 1
        if self.outer_table.size_index == len(self.outer_table.TABLE_SIZES):
            # Cannot be resized further.
            return
        self.outer_table.array = ArrayR(self.outer_table.TABLE_SIZES[self.outer_table.size_index])
        self.outer_table.count = 0

        for item in temp_copy:
            if item is not None:
                key, value = item
                self.outer_table.hash = lambda k: self.hash1(key)
                self.outer_table[key] = value

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.outer_table.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.outer_table.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()


class HashTableIterator(Generic[T]):
    def __init__(self, table) -> None:
        self.current = table
        self.index = -1

        self.values = False
        self.outer = False
        self.outer_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if not self.values:
            self.index += 1
            if self.index == self.current.table_size:
                raise StopIteration
            else:
                item = self.current.array[self.index]
                while True:
                    if item is None:
                        self.index += 1
                        if self.index == self.current.table_size:
                            raise StopIteration
                        item = self.current.array[self.index]
                        if item is not None:
                            return item[0]
                    else:
                        self.index += 1
                        return item[0]
        else:
            if self.outer:
                if self.outer_index == self.current.table_size:
                    raise StopIteration

                # Keep looping outer table till we find a tuple
                while True:
                    item = self.current.array[self.outer_index]
                    if item is None:
                        self.outer_index += 1
                        if self.outer_index == self.current.table_size:
                            raise StopIteration
                    else:
                        inner_table = item[1]
                        while True:
                            item2 = inner_table.array[self.inner_index]
                            if item2 is None:
                                self.inner_index += 1
                                if self.inner_index == inner_table.table_size:
                                    self.outer_index += 1
                                    self.inner_index = 0
                                    break
                            else:
                                self.inner_index += 1
                                if self.inner_index == inner_table.table_size:
                                    self.outer_index += 1
                                    self.inner_index = 0
                                return item2[1]
            else:
                self.index += 1
                if self.index == self.current.table_size:
                    raise StopIteration
                else:
                    item = self.current.array[self.index]
                    while True:
                        if item is None:
                            self.index += 1
                            if self.index == self.current.table_size:
                                raise StopIteration
                            item = self.current.array[self.index]
                            if item is not None:
                                return item[1]
                        else:
                            self.index += 1
                            return item[1]


