from __future__ import annotations

from mountain import Mountain
from algorithms.mergesort import mergesort


class MountainOrganiser:

    def __init__(self) -> None:
        self.mountains = []

    def cur_position(self, mountain: Mountain) -> int:
        """
        This will return the index/position (Rank) of the given mountain from within the mountain organiser

         Complexity analysis:
        --------------------
        Best case: O(1) if there is only 1 mountain in the self.mountains list
        Worst case: O(n) if there are n mountains in self.mountains list
        """
        if mountain not in self.mountains:
            raise KeyError(mountain)
        else:
            return self.mountains.index(mountain)

    def add_mountains(self, mountains: list[Mountain]) -> None:
        """
        Adds a list of mountains to add to our mountain organiser without adding duplicate mountains
        and sorts them in ascending order based on the mountain length.

        Complexity analysis:
        --------------------
        Best case: O(1) if there is only 1 mountain in the self.mountains list
        Worst case: O(Mlog(M) + N) for N mountains in the mountains list and Mlog(M) for the self.mountains of length M
        """
        # The for loop has a complexity of:
        # Best case: O(1) if only 1 mountain in the list
        # Worst case: O(n) if n mountains in the list
        for mountain in mountains:
            if mountain not in self. mountains:
                self.mountains.append(mountain)

        # Sort the mountains in self.mountains in ascending order based on each mountains length
        # The complexity of the mergesort is:
        # Best case: O(1) if the self.mountains list only has 1 mountain
        # Worst case: O(Mlog(M)) if there are M mountains in self.mountains list
        self.mountains = mergesort(self.mountains)
