from mountain import Mountain
from data_structures.hash_table import LinearProbeTable
from mountain_organiser import MountainOrganiser


class MountainManager:

    def __init__(self) -> None:
        self.manager = LinearProbeTable()
        self.organiser = MountainOrganiser()

    def add_mountain(self, mountain: Mountain) -> None:
        """
        Complexity Analysis:
        --------------------
        Best case: O(hash(key)) first position is empty for the manager (LinearProbeTable) and the organiser list (MountainOrganiser) is empty
        Worst case: O(hash(key) + N*comp(K)) when we've searched the entire table where N is the table size for self.manager
                    + O(Mlog(M) + N) for N mountains in the mountains organiser list and Mlog(M) for the self.mountains of length M
        """
        self.manager[mountain.name] = mountain
        self.organiser.add_mountains([mountain])

    def remove_mountain(self, mountain: Mountain) -> None:
        """
        Complexity Analysis:
        --------------------
        Best case: O(hash(key)) when there is only 1 mountain to remove from the manager and organiser
        Worst Case: O((N*hash(key)+N^2*comp(K)) + N)
                    for removing an item from manager --> O(N*hash(key)+N^2*comp(K)) deleting item is midway through large chain.
                    for removing an item from the organiser list --> O(N)
        """
        self.organiser.mountains.remove(mountain)
        del self.manager[mountain.name]

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        """
        Complexity Analysis:
        --------------------
        Best case: O(1) is there is only 1 mountain in both the manager and the organiser to edit
        Worst Case: O(index(array) + N) where N is the length of the manager table size
        """
        self.organiser.mountains[self.organiser.mountains.index(old)] = new
        # self.manager[old.name] = new
        for i in range(self.manager.table_size):
            if self.manager.array[i] is not None:
                if self.manager.array[i][1] == old:
                    self.manager.array[i] = (new.name, new)
                    break

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        """
        Complexity Analysis:
        --------------------
        Best case: O(1) when there is only 1 mountain in the organiser list
        Worst Case: O(N) when N is the length of the organiser list and we need to traverse all the items in the list
        """
        mountains_with_difficulty = []
        for mountain in self.organiser.mountains:
            if mountain.difficulty_level == diff:
                mountains_with_difficulty.append(mountain)
        return mountains_with_difficulty

    def group_by_difficulty(self) -> list[list[Mountain]]:
        """
        Returns a list of lists of all mountains, grouped by and sorted by ascending difficulty.

        Complexity Analysis:
        --------------------
        Best case: O(1) when there is only one mountain in the organiser
        Worst Case: O(N + M*N) where N is the length of the organiser list and M is the range of the difficulty levels
        """
        diff_groups = []

        # Finding the highest difficulty
        max_diff = 0
        for mountain in self.organiser.mountains:
            if mountain.difficulty_level > max_diff:
                max_diff = mountain.difficulty_level

        for i in range(max_diff+1):
            temp = []
            for mountain in self.organiser.mountains:
                if mountain.difficulty_level == i:
                    temp.append(mountain)
            if temp:
                diff_groups.append(temp)

        return diff_groups
