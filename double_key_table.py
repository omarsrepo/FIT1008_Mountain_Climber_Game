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

        Complexity Analysis:
        --------------------
        Best case: O(len(key1) + len(key2)) when the positions in the outer table and inner table are empty
        Worst case: O(N*len(key1) + M*len(key2)) where N = size of outer array and M = size of inner array.

                    Worst case is when the outer table and inner table are full or if the outer key and inner key are
                    at positions (outer_index-1) and (inner_index-1) so the linear probe has to wrap around the table
                    and keep searching till length of list to find the outer and inner keys to update their values.
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

        Complexity Analysis:
        --------------------
        Best case: O(N) where N is outer table size and when key = None. Simply return all the keys in the outer table
        Worst case: O(N*len(K1) + M) where N is length of outer table and M is length of internal table.

                    Worst case happens when the outer key is at position (hash1(key)-1) which means the linear probe function
                    has to wrap around the outer table and iterate through the whole thing to find the position of the outer key.
                    It then has to access the internal table associated with outer key and iterate through the whole internal table
                    to append all the keys to the key list.
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

        Complexity Analysis:
        --------------------
        Best case: O(M) where M is the length of the inner table and when the outer key is at the correct
                   index provided by the hash function which allows us to immediately access the inner table.
                   The only step left is to iterate through the inner table and append all the values to the values list.

        Worst case: O(N + P*(N*len(Key) + M)) where N is length of outer table, P is length of keys list and M is the length of interal table.

                    This happens when we no Key = None and we have to first get a list of all the keys in the outer table.
                    We then have to iterate through all the keys in the key list and probe for their locations and then once we get
                    their locations, we have to access their associated internal table and iterate through the entire internal table
                    and append all the values to the values list.
        """
        values = []
        if key is None:
            # Get a list of all the keys in the outer table
            keys = self.keys()
            # Iterate through all the internal tables for each external key
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.

        Complexity Analysis: (Same as Linear Probe)
        --------------------
        Best case: O(len(key1) + len(key2)) when the positions in the outer table and inner table are empty
        Worst case: O(N*len(key1) + M*len(key2)) where N = size of outer array and M = size of inner array.

                    Worst case is when the outer table and inner table are full or if the outer key and inner key are
                    at positions (outer_index-1) and (inner_index-1) so the linear probe has to wrap around the table
                    and keep searching till length of list to find the outer and inner keys to update their values.
        """
        positions = self._linear_probe(key[0], key[1], False)
        return self.outer_table.array[positions[0]][1].array[positions[1]][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set a (key, value) pair in our hash table.

        Complexity Analysis:
        --------------------
        Best case: O(len(key1) + len(key2)) when the positions in the outer table and inner table are empty and the outer table and inner tablers
                   have not exceeded their load factors
        Worst case: O(N*len(key1) + M*len(key2)) where N = size of outer array and M = size of inner array.
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

        Complexity Analysis:
        --------------------
        Best case: O(len(key1) + len(key2) + hash(key2))
        Worst case: O(N*len(key1) + M*len(key2) + (N*hash(key)+N^2*comp(K))) : see complexity of _linear_probe and LinearProbeTable deleteitem method
        """
        # The contains magic method will raise the key errors if the keys don't exist
        positions = self._linear_probe(key[0], key[1], False)
        inner_table = self.outer_table.array[positions[0]][1]
        inner_table.hash = lambda k: self.hash2(k, inner_table)

        del inner_table[key[1]]  # complexity: O(hash(key[1])) / O(N*hash(key)+N^2*comp(K))

        if inner_table.count == 0:
            self.outer_table.array[positions[0]] = None
            self.outer_table.count -= 1

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        Complexity Analysis:
        --------------------
        Best case: O(T * (len(key1) + len(key2)) Where T is the length of the outer array before resizing and the (len(key1)+len(key2)) is the
                   complexity of the setitem method for each key, value pair from the temp_copy array.
        Worst case: Same as Best case because the for loop sets the key,value pairs into a new empty resized array so there will be less chances
                    of collisions.
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


if __name__ == '__main__':
    dt = DoubleKeyTable(sizes=[12], internal_sizes=[5])
    dt.hash1 = lambda k: ord(k[0]) % 12
    dt.hash2 = lambda k, sub_table: ord(k[-1]) % 5

    dt["May", "Jim"] = 1
    dt["Kim", "Tim"] = 2

    for item in dt.outer_table.array:
        print(item)
    print()










