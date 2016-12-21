"""Move histories. Eschewed in favor of nested lists since Python slow.

Jason Mahr
"""


from random import random
from time import clock


class Move:
    """Move IDs range from 0 to 17."""
    def __init__(self, id=None, next=None):
        self.id = id
        self.next = next
    
    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_next(self):
        return self.next

    def set_next(self, next):
        self.next = next


class History:
    def __init__(self):
        self.head = None

    def add(self, id):
        move = Move(id)
        move.set_next(self.head)
        self.head = move

    def clear(self):
        self.head = None

    def copy(self, other):
        self.head = other.head
        
    def get(self):
        size = self.size()
        moves = [None] * size
        ptr = self.head
        for i in range(size):
            moves[i] = ptr.id
            ptr = ptr.next
        return moves

    def size(self):
        """This function removes redundancies from a move history in
        place, returning the resulting number of moves. Redundancies
        removed include pairs (e.g. l l' -> nothing) and sandwiches
        (e.g. l2 r2 l' -> l r2). See Section 4.2 of the paper for more
        details.
        
        Removing redundancies is necessary since size is incorporated
        into fitness scores, and also so that the solution received by
        the end user is not redundant.
        """

        """The prepended anchor is used to track the head and later
        deleted. This simplifies the code for redundancies at the start
        that disappear. For example, for L2 L2 U, we prepend a move
        first, so we have None L2 L2 U. Then the None pointer can point
        to U as if this was in the middle of the move sequence, and we
        do not need to program another step for heads of lists. Before
        returning, the function will promote `self.history`, in effect
        removing the prepended anchor.
        """
        current = self.head
        self.add(None)
        previous = self.head

        """Size is used to track whether a change has been made. If a
        change is made, size is set to 0. If no change has yet been
        made, size is positive, and with each new move seen, size will
        increment by 1 if it is positive. Thus, size serves two
        functions. If it is 0 at the end of the loop, a change was made,
        and we repeat the loop. If it is not 0, it will be the size of
        the move history.

        It is important to restart from the beginning of the move
        history when there is a change. For example, consider the move
        sequence L2 F2 U2 U2 F2 L2. This is completely redundant, but
        the `current` pointer will be at U2 by the time we find a
        redundancy, and `previous` would be pointing to F2. There would
        be nothing pointing to L2, so we would need to repeat from the
        beginning. More pointers will not help since the nesting could
        be arbitrarily deep.
        """
        size = 0
        while not size:
            size = 1

            # While current and next are not None
            # Need the current in case move history is empty
            while current and current.next:
                if current.id // 3 == current.next.id // 3:
                    size = 0
                    current_mod = current.id % 3
                    mod_sum = current_mod + current.next.id % 3
                    if mod_sum == 2:
                        current = current.next.next
                        previous.next = current
                    else:
                        current.id += (mod_sum + 1) % 4 - current_mod
                        current.next = current.next.next

                elif (current.id // 6 == current.next.id // 6 and
                      current.next.next and
                      current.id // 3 == current.next.next.id // 3):
                    size = 0
                    current_mod = current.id % 3
                    mod_sum = current_mod + current.next.next.id % 3
                    if mod_sum == 2:
                        current.id = current.next.id
                        current.next = current.next.next.next
                    else:
                        current.id += (mod_sum + 1) % 4 - current_mod

                        """We need a copy of the next node that instead
                        points to the next-next-next node as opposed to
                        the next-next node, since the current node and
                        the next-next node are turning the same side and
                        the next node is the opposite side, making the
                        next-next node redundant for this cube history.

                        However, recall that these histories are shared!
                        Thus we cannot actually edit the next node,
                        since there could be another cube whose move
                        history starts there, and then that cube will
                        lose its second move. Hence the copy.
                        """
                        new_next = Move(current.next.id)
                        new_next.set_next(current.next.next.next)
                        current.next = new_next
                        
                else:
                    if size:
                        size += 1
                    previous = current
                    current = current.next

            # Prepare for next loop
            previous = self.head
            current = previous.next
            
        # Clean up by removing prepended anchor for previous and return
        self.head = self.head.next
        
        # Need to return 0 if self.head is None; it is 1 from the loop
        return size if self.head else 0
