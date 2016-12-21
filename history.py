"""Move histories as nested lists. Linked lists were tried as an
experiment. See Section 4.2 of the paper for more details.

Jason Mahr
"""


from constants import MOVES


class History:
    """This encodes a move history. Each cube has a history, and the
    memory for the moves themselves are shared.
    """
    def __init__(self):
        self.history = None
    
    def add(self, move):
        self.history = [move, self.history]
    
    def clear(self):
        self.history = None

    def get_ptr(self):
        return self.history

    def copy(self, other):
        self.history = other.get_ptr()

    def get(self):
        """Returns moves as a list of strings in reverse (correct) order
        after first removing redundancies.
        """
        size = self.size()
        moves = [None] * size
        ptr = self.history
        for i in range(size - 1, -1, -1):
            moves[i], ptr = MOVES[ptr[0]], ptr[1]
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
        current = self.history
        self.add(None)
        previous = self.history

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

            """While current and current[1] are not None. Current needs
            to be checked since the move history could have been empty.
            """
            while current and current[1]:
                if current[0] // 3 == current[1][0] // 3:

                    """If two back-to-back moves are of the same face,
                    they are redundant. Set size to 0 to record this.
                    
                    A move ID integer-divided by 3 indicates its face,
                    and modded by 3 indicates whether it is clockwise
                    (0), half (1), or counterclockwise (2).

                    The math removes both moves if their sum after %3 is
                    2, which could result from 02, 11, or 20, all of
                    which are totally redundant.

                    If the sum of the mods is not 2, there are a few
                    possibilities:
                        0 -> two clockwise turns; combine to 1
                        1 -> one clockwise one half; combine to 2
                        3 -> one half one counterclockwise; combine to 0
                        4 -> two counterclockwise; combine to 1
                    Note: we can get from the mod sum to the combined
                    value by taking (mod_sum + 1) % 4.

                    Now, current[0] is not necessarily 0, 1, or 2, it
                    could be 12, 13, 14. So we need to subtract
                    current_mod from the combined new value, and add
                    that to the current value. Then we redirect the
                    pointer to skip the second move.
                    """
                    current_mod = current[0] % 3
                    mod_sum = current_mod + current[1][0] % 3
                    if mod_sum == 2:
                        # Remove both moves from the sequence.
                        current = current[1][1]
                        previous[1] = current
                    else:
                        # Update according to above comment.
                        current[0] += (mod_sum + 1) % 4 - current_mod
                        current[1] = current[1][1]

                    # Record that we made a change and need to revisit.
                    size = 0

                elif (current[0] // 6 == current[1][0] // 6 and
                      current[1][1] and
                      current[0] // 3 == current[1][1][0] // 3):

                    """If we have a sandwich, much of the logic is the
                    same, just we need to create a new node for the
                    second case, as described in the next comment.
                    """
                    current_mod = current[0] % 3
                    mod_sum = current_mod + current[1][1][0] % 3
                    if mod_sum == 2:
                        
                        # If LRL'U, set the L to R, and point it to U.
                        current[0] = current[1][0]
                        current[1] = current[1][1][1]
                    else:
                        
                        current[0] += (mod_sum + 1) % 4 - current_mod

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
                        current[1] = [current[1][0], current[1][1][1]]

                    # Record that we made a change.
                    size = 0
                    
                else:
                
                    # If no redundancies, and no changes yet, increment.
                    if size:
                        size += 1
                    previous, current = current, current[1]

            # Prepare for next loop in case size is 0.
            previous = self.history
            current = previous[1]

        # Clean up by removing prepended anchor
        self.history = self.history[1]

        """Return. Since the size was made to be 1 in order to check
        for changes, if `self.history` = None we need to return 0
        instead of size.
        """
        return size if self.history else 0
