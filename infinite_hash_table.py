from __future__ import annotations
from typing import Generic, TypeVar

import data_structures.referential_array
from data_structures.referential_array import ArrayR
from data_structures.linked_stack import LinkedStack

K = TypeVar("K")
V = TypeVar("V")


class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise, `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self) -> None:
        self.array = ArrayR(self.TABLE_SIZE)
        self.level = 0
        self.container = LinkedStack()
        self.switch = True
        self.count = 0

        # This is just a list of all the keys in the table
        self.keys = []

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        table = self.array
        indexes = self.get_location(key)
        for i in indexes:
            table = table[i]
        return table[1]

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set a (key, value) pair in our hash table.

        Complexity Analysis:
        --------------------

        """
        table = self.array
        if key not in self.keys:
            self.keys.append(key)

        while True:
            position = self.hash(key)

            if table[position] is None:
                table[position] = (key, value)
                self.level = 0
                self.count += 1
                break
            elif isinstance(table[position], tuple):

                if table[position][0] == key:
                    table[position] = (key, value)  # Simply update the key's value if the key already exists
                    self.level = 0
                    return

                self.container.push((key, value))
                self.container.push(table[position])
                table[position] = ArrayR(self.TABLE_SIZE)

                table = table[position]
                self.level += 1

                while True:
                    if self.get_level():
                        for i in range(len(self.container)):
                            key, value = self.container.pop()
                            position = self.hash(key)
                            table[position] = (key, value)
                        self.count += 1
                        self.level = 0
                        return
                    else:
                        position = self.hash(key)
                        table[position] = ArrayR(self.TABLE_SIZE)
                        table = table[position]
                        self.level += 1
            else:
                table = table[position]
                self.level += 1

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        values = []
        if key in self.keys:
            self.keys.remove(key)
            # Re-insert all the remaining key value pairs
            for key in self.keys:
                value = self[key]
                values.append(value)
        else:
            raise KeyError(key)

        self.array = ArrayR(self.TABLE_SIZE)
        self.count = 0
        for i in range(len(self.keys)):
            self[self.keys[i]] = values[i]

    def __len__(self):
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()

    def __contains__(self, key: K) -> bool:
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

    def get_location(self, key) -> list:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        self.level = 0
        table = self.array
        index_list = []
        while True:
            position = self.hash(key)
            index_list.append(position)

            if table[position] is None:
                self.level = 0
                raise KeyError(key)
            elif isinstance(table[position], tuple):
                if table[position][0] == key:
                    self.level = 0
                    return index_list
                else:
                    raise KeyError(key)
            else:
                table = table[position]
                self.level += 1

    def get_level(self) -> bool:
        """
        This function returns a boolean value that says:

        True: If the keys can be hashed into the current level without any collisions
        False: If the keys cannot be hashed into the current level without any collisions (different keys generates same hash position)
        """
        index_list = []
        temp = LinkedStack()

        for i in range(len(self.container)):
            item = self.container.peek()
            temp.push(item)
            self.container.pop()
            index_list.append(self.hash(item[0]))
        for i in range(len(temp)):
            self.container.push(temp.peek())
            temp.pop()

        if len(set(index_list)) == len(index_list):
            return True
        else:
            return False
