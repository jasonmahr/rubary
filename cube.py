"""This module implements the structure of a Rubik's cube.

Jason Mahr
"""


from constants import *
from history import History
from random import random


class Cube:
    """Representation of a Rubik's Cube."""


    def __init__(self):
        """Initializes a Rubik's Cube with cube, moves, fitness, and
        num_moves."""


        """Cube: There is no use for an algorithm to consider whole-cube
        rotations when solving a cube, so without loss of generality
        assume sides never switch positions.

        This means center tiles never move, so 8 tile colors is
        sufficient to characterize a side.

        Indeces are oriented as follows, with L, R, F, B, U, and D
        representing each side (left, right, front, back, up, down) in
        accordance with standard Rubik's Cube move notation.

                      |-------------|
                      || 0 | 1 | 2 ||
                      || 7 | U | 3 ||
                      || 6 | 5 | 4 ||
        |-------------|-------------|-------------|-------------|
        || 0 | 1 | 2 ||| 0 | 1 | 2 ||| 0 | 1 | 2 ||| 0 | 1 | 2 ||
        || 7 | L | 3 ||| 7 | F | 3 ||| 7 | R | 3 ||| 7 | B | 3 ||
        || 6 | 5 | 4 ||| 6 | 5 | 4 ||| 6 | 5 | 4 ||| 6 | 5 | 4 ||
        |-------------|-------------|-------------|-------------|
                      || 0 | 1 | 2 ||
                      || 7 | D | 3 ||
                      || 6 | 5 | 4 ||
                      |-------------|

        The cube is stored as a 2D array. Sides are stored separately to
        help with certain algorithms that cycle through an entire side
        at a time (e.g. rotate a side).
        
        Sides are arbitarily ordered as L, R, F, B, U, D, but henceforth
        in the code the constants L, R, F, B, U, D are used instead of
        integer indeces to improve readbility.
        """
        self.cube = [[side] * 8 for side in range(6)]


        """Move history: Moves are stored as linked-list style data
        structures in reverse order.

        Storing in reverse order allows cubes to add moves to shared
        move histories without conflicts. New moves are simply prepended
        onto the list. This allows a cube to simply copy a pointer when
        copying another cube, as opposed to each cube storing its own
        history, which would waste a lot of memory and also time when
        copying another cube. More details are availble in Section 4.2
        of the paper.        
        """
        self.history = History()


        """Fitness: The fitness score incorporates both the score from
        the fitness functions in fitness.py as well as the size of the
        cube's move sequence in order to avoid solutions that are
        unnecessarily long. `self.fitness_score` holds this value, which
        is how cubes are compared.

        `self.fitness` stores the result of the fitness function only,
        without regard to the length of the cube's move sequence. The
        purpose of this is to be able to easily figure out when a cube
        has satisfied the requirements of a particular phase. It also is
        more informative when displayed to the user in progress updates.
        """
        self.fitness = 0
        self.fitness_score = 0


    """Data I/O. Prevents other code from directly accessing attributes.
    """


    def get(self, (side, index)):
        """Returns the color of a tile.
        
        0 means the color of the left side's center tile, 1 means the
        color of the right side's center tile, etc.
        
        Use: self.get_tile(U3) to get the color of the tile at position
        U3. Useful for fitness functions.
        """
        return self.cube[side][index]

    
    def set(self, (side, index), color):
        self.cube[side][index] = color

    
    def get_cube(self):
        return [side[:] for side in self.cube]

    
    def get_history(self):
        return self.history.get()


    def get_history_ptr(self):
        return self.history


    def clear_history(self):
        self.history.clear()


    def size(self):
        return self.history.size()


    def get_fitness(self):
        return self.fitness
        
    
    def set_fitness(self, fitness):
        self.fitness = fitness


    def get_fitness_score(self):
        return self.size
        
    
    def set_fitness_score(self, fitness_score):
        self.fitness_score = fitness_score
    

    """Moves

    Three private helper functions followed by the main move function.
    """


    def __cw(self, side):
        """Executes a clockwise turn of the specified side."""


        """First, rotate the 8 colors of the given side's face clockwise
        (clockwise when looking at the given face).

        Example: For the left face,
            0 1 2             6 7 0
            7 L 3   becomes   5 L 1
            6 5 4             4 3 2.

        To visualize this, the tile labels in both diagrams correspond
        to the original colors at each position, so that L6 means the
        color originally at L6 in both diagrams. Position is implied.
        """
        self.cube[side] = [self.cube[side][i] for i in 6, 7, 0, 1, 2, 3, 4, 5]


        """Next, we need to shift the values of the tiles on the 4 sides
        that border the turning side.

        Example: For the left face,
                      U   6                                 B   2
                      7        0                            3        0
                  0              F                      4              U
                               7                                     7

              2                6       becomes      6                6

              3                                     7
            B               0                     D               0
              4         7                           0         7
                    6   D                                 6   F

        To visualize this, imagine the left side is an inch in front of
        the monitor, and these are the colors immediately bordering the
        left side. As shown, a clockwise turn of the left side brings
        the front side's bordering tiles to the down side, the down
        side's bordering tiles to the back side, etc. As with before,
        the labels correspond to the original colors, not position.

        Note the back indices are 2, 3, 4 and not 6, 7, 0. B0 is far
        behind the monitor bordering the right side, which is farthest
        away, and the up side.

        Importantly, there are 3 4-cycles that shift to the right:
        Front 6, down 6, back 2, up 6
        Front 7, down 7, back 3, up 7
        Front 0, down 0, back 4, up 0.

        Notice how the indices are increasing by 1 (mod 8) for all
        sides. In fact, the original clockwise indexing was chosen for
        this property. No matter which side is being turned, the
        bordering indices always correspond such that they increment by
        1 (mod 8) together.

        Thus we can specify the 3 4-cycles simply by specifying one:
        F6, D6, B2, U6

        This is precisely the value of the constant CW_BORDERS_OF[L] (!)

        Since we are rotating clockwise, we shift according to the
        pattern
            front, down, back, up = up, front, down, back
            (1, 2, 3, 4 = 4, 1, 2, 3)
        for each of the 3 4-cycles.
        """
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            (self.cube[s1][i1], self.cube[s2][i2], self.cube[s3][i3],
             self.cube[s4][i4]) = (self.cube[s4][i4], self.cube[s1][i1],
                                   self.cube[s2][i2], self.cube[s3][i3])
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]


    def __half(self, side):
        """Executes a half turn, which means two clockwise turns."""


        # Rotate the 8 colors of the given side's face
        self.cube[side] = [self.cube[side][i] for i in 4, 5, 6, 7, 0, 1, 2, 3]


        """Shift border values. This is done the same way as before,
        except that instead of
            front, down, back, up = up, front, down, back
            (1, 2, 3, 4 = 4, 1, 2, 3),
        we use
            front, down, back, up = back, up, front, down
            (1, 2, 3, 4 = 3, 4, 1, 2).
        Opposites switch, which is what happens when a side is rotated
        twice.
        """
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            (self.cube[s1][i1], self.cube[s2][i2], self.cube[s3][i3],
             self.cube[s4][i4]) = (self.cube[s3][i3], self.cube[s4][i4],
                                   self.cube[s1][i1], self.cube[s2][i2])
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]



    def __ccw(self, side):
        """Executes a counterclockwise turn.
        
        1, 2, 3, 4 = 2, 3, 4, 1 for counterclockwise turns.
        """
        self.cube[side] = [self.cube[side][i] for i in 2, 3, 4, 5, 6, 7, 0, 1]
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            (self.cube[s1][i1], self.cube[s2][i2], self.cube[s3][i3],
             self.cube[s4][i4]) = (self.cube[s2][i2], self.cube[s3][i3],
                                   self.cube[s4][i4], self.cube[s1][i1])
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]
        
    
    def move(self, move_id):
        """Executes the move corresponding to a specified move_id.

        The correspondances are as follows:

        0: l       3: r       6: f        9: b       12: u       15: d
        1: l2      4: r2      7: f2      10: b2      13: u2      16: d2
        2: l'      5: r'      8: f'      11: b'      14: u'      17: d'

        As per standard Rubik's Cube notation, no decoration denotes a
        clockwise turn, a 2 denotes a half turn, and an apostrophe
        denotes a counterclockwise turn.
        """
        side = move_id // 3
        rotation = move_id % 3
        if not rotation:
            self.__cw(side)
        elif rotation == 1:
            self.__half(side)
        else:
            self.__ccw(side)
        self.history.add(move_id)


    def scramble(self):
        """Executes 100 non-redundant random moves.

        20 moves is enough to get to every possible Rubik's Cube
        configuration. 100 moves is more than enough for randomness.

        Result is printed to the terminal to help with testing.
        """
        self.reset()
        while self.size() < 100:
            self.move(int(random() * 18))
        moves_made = self.get_history()
        self.clear_history()
        print 'Scramble:', moves_made
        

    """Cube Operations"""


    def reset(self):
        self.__init__()


    def copy(self, other):
        self.cube = other.get_cube()
        self.history.copy(other.get_history_ptr())
        self.fitness = other.get_fitness()
        self.fitness_score = other.get_fitness_score()
