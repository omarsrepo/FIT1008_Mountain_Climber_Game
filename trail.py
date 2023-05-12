from __future__ import annotations
from dataclasses import dataclass


from mountain import Mountain
from data_structures.linked_stack import Node, LinkedStack

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality


@dataclass
class TrailSplit:
    """
    A split in the trail.
       ___path_top____
      /               \
    -<                 >-path_follow-
      \__path_bottom__/
    """

    path_top: Trail
    path_bottom: Trail
    path_follow: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.path_follow.store


@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--
    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """Removes the mountain at the beginning of this series."""
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        return TrailSeries(mountain, Trail(TrailSeries(self.mountain, self.following)))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        """self = TrailSplit(Trail(None), Trail(None), Trail(TrailSeries(self.mountain, self.following)))
        return self"""
        return TrailSplit(Trail(None), Trail(None), Trail(TrailSeries(self.mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
        new_branch = Trail(TrailSplit(Trail(None), Trail(None), self.following))
        # self.following = Trail(TrailSplit(Trail(None), Trail(None), self.following))
        return TrailSeries(self.mountain, new_branch)


TrailStore = Union[TrailSplit, TrailSeries, None]


@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """Adds a mountain before everything currently in the trail."""
        self.store = TrailSeries(mountain, Trail(None))
        return self

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        self.store = TrailSplit(Trail(None), Trail(None), Trail(None))
        return self

    def follow_path(self, personality: WalkerPersonality) -> None:
        """
        Follow a path and add mountains according to a personality.

        Complexity Analysis:
        --------------------
        Best case: O(N) if the personalities are TopWalker or BottomWalker and where N is the number of TrailStores in the trail
        Worst case: O(N * LazyWalker) if the personality is LazyWalker and where N is the number of TrailStores in the trail
        """
        current = self.store
        follows = LinkedStack()

        while True:
            if isinstance(current, TrailSplit):
                follows.push(Node(current.path_follow))  # Add the TrailSplit follow path to a linked stack
                if personality.select_branch(current.path_top, current.path_bottom):
                    current = current.path_top.store
                else:
                    current = current.path_bottom.store

            elif isinstance(current, TrailSeries):
                personality.add_mountain(current.mountain)
                if current.following.store is None:
                    if len(follows) > 0:
                        current = follows.pop().item.store
                    else:
                        break
                else:
                    current = current.following.store

            elif current is None:
                if len(follows) > 0:
                    current = follows.pop().item.store
                else:
                    break
        follows.clear()  # Make sure the linked stack is cleared after being used

    def collect_all_mountains(self) -> list[Mountain]:
        """
        Returns a list of all mountains on the trail.

        Complexity Analysis:
        --------------------
        Best case: O(1) if there is only one TrailSeries in the Trail
        Worst case: O(N) where N is the no.of nodes (TrailSeries/TrailSplit) in the Trail
        """
        current = self.store
        test_list = []
        temp_stack = LinkedStack()

        while True:
            if isinstance(current, TrailSeries):
                test_list.append(current.mountain)
                current = current.following.store
                if current is None:
                    if len(temp_stack) > 0:
                        current = temp_stack.pop()
                        continue
                    break
            elif isinstance(current, TrailSplit):
                temp_stack.push(current.path_follow.store)
                temp_stack.push(current.path_bottom.store)
                current = current.path_top.store
            else:
                if len(temp_stack) > 0:
                    current = temp_stack.pop()
                else:
                    break

        return test_list

    def length_k_paths(self, k) -> list[list[Mountain]]:  # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.

        The traverse function iteratively travels the path while recording the direction of the mountains in
        current_path. The current path is added to the list of paths if there is no more distance to cover. The
        function recursively walks both branches if the current store is a TrailSplit and neither branch is None.
        The current mountain is added to the current path if the current store is a TrailSeries, and if it is not
        None, the function recursively explores the subsequent trail. The current mountain is then removed from the
        route before turning around.
        """
        def traverse(current: TrailStore, remaining: int, current_path: list[Mountain], follows: LinkedStack) -> None:
            if remaining == 0:
                return

            if isinstance(current, TrailSplit):
                follows.push(current.path_follow.store)
                if current.path_top.store is not None:
                    traverse(current.path_top.store, remaining, current_path, follows)
                if current.path_bottom.store is not None:
                    traverse(current.path_bottom.store, remaining, current_path, follows)

            elif isinstance(current, TrailSeries):
                current_path.append(current.mountain)
                if current.following.store is not None:
                    traverse(current.following.store, remaining - 1, current_path, follows)
                else:
                    if not follows.is_empty():
                        current = follows.pop()
                        traverse(current, remaining - 1, current_path, follows)
            else:
                if not follows.is_empty():
                    current = follows.pop()
                    traverse(current, remaining, current_path, follows)

        current = self.store
        current_path = []
        follows = LinkedStack()
        traverse(current, k, current_path, follows)
        return current_path
    
