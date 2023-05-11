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
        Best case:
        Worst Case:
        """
        self.manager[mountain.name] = mountain
        self.organiser.add_mountains([mountain])

    def remove_mountain(self, mountain: Mountain) -> None:
        """
        Complexity Analysis:
        --------------------
        Best case:
        Worst Case:
        """
        self.organiser.mountains.remove(mountain)
        del self.manager[mountain.name]

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        """
        Complexity Analysis:
        --------------------
        Best case:
        Worst Case:
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
        Best case:
        Worst Case:
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
        Best case:
        Worst Case:
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


if __name__ == "__main__":
    """
    MountainManager.manager = InfiniteHashTable()
    MountainManager.manager.array = ArrayR(27)
    """
    m1 = Mountain("m1", 2, 2)
    m2 = Mountain("m2", 2, 9)
    m3 = Mountain("m3", 3, 6)
    m4 = Mountain("m4", 3, 1)
    m5 = Mountain("m5", 4, 6)
    m6 = Mountain("m6", 7, 3)
    m7 = Mountain("m7", 7, 7)
    m8 = Mountain("m8", 7, 8)
    m9 = Mountain("m9", 7, 6)
    m10 = Mountain("m10", 8, 4)

    mm = MountainManager()
    mm.add_mountain(m1)
    mm.add_mountain(m2)
    mm.add_mountain(m3)
    mm.add_mountain(m4)
    mm.add_mountain(m5)
    mm.add_mountain(m6)
    mm.add_mountain(m7)

    # for item in mm.manager.array:
    #     print(item)
    #
    # del mm.manager[m1.name]
    # print()
    #
    # for item in mm.manager.array:
    #     print(item)
