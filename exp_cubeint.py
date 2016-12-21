"""An experiment using ints instead of lists for cube sides. Performance
was ultimately worse.

Jason Mahr
"""


from constants import *
from history import History
from random import random


def int_to_list(side):
    return [side // 6 ** i % 6 for i in range(8)]


def p(cube):
    print [int_to_list(side) for side in cube.cube]


class Cube:
    """Representation of a Rubik's Cube."""

    def __init__(self):
        """Initializes a Rubik's Cube with cube, moves, fitness, and
        num_moves.
        """
        self.cube = [0] * 6
        self.history = History()
        self.fitness = 0
        self.fitness_score = 0

    def get_history(self):
        return self.history.get()

    def size(self):
        return self.history.size()

    def clear_history(self):
        self.history.clear()

    def get_fitness(self):
        return self.fitness

    def set_fitness(self, fitness):
        self.fitness = fitness
    
    def get_fitness_score(self):
        return self.size
    
    def set_fitness_score(self, fitness_score):
        self.fitness_score = fitness_score

    def reset(self):
        self.cube = [(6 ** 8 - 1) * i / 5 for i in range(6)]
        self.history.clear()
        self.fitness = 0
        self.fitness_score = 0

    def copy(self, other):
        self.cube[:] = other.cube
        self.history.copy(other.history)


    """Get, put"""


    def get(self, (side, index)):
        return self.cube[side] // 6 ** index % 6

    def put(self, new_color, (side, index)):
        orig_color = self.get((side, index))
        self.cube[side] += (new_color - orig_color) * 6 ** index
        return orig_color

    def num_errors(self):
        num = 0
        for side in range(6):
            for index in range(8):
                if self.get((side, index)) != side:
                    num += 1
        return num
    
    def is_solved(self):
        return not self.num_errors()


    """Moves"""


    def cycle2(self, t1, t2):
        self.put(self.put(self.get(t1), t2), t1)
    
    def cycle4(self, t1, t2, t3, t4):
        self.put(self.put(self.put(self.put(self.get(t1), t2), t3), t4), t1)
    
    def cw(self, side):
        # Rotate face.
        self.cycle4((side, 0), (side, 2), (side, 4), (side, 6))
        self.cycle4((side, 1), (side, 3), (side, 5), (side, 7))

        # Rotate borders.
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            self.cycle4((s1, i1), (s2, i2), (s3, i3), (s4, i4))
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]
    
    def half(self, side):
        # Rotate face.
        self.cycle2((side, 0), (side, 4))
        self.cycle2((side, 1), (side, 5))
        self.cycle2((side, 2), (side, 6))
        self.cycle2((side, 3), (side, 7))

        # Rotate borders.
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            self.cycle2((s1, i1), (s3, i3))
            self.cycle2((s2, i2), (s4, i4))
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]

    def ccw(self, side):
        # Rotate face.
        self.cycle4((side, 6), (side, 4), (side, 2), (side, 0))
        self.cycle4((side, 7), (side, 5), (side, 3), (side, 1))

        # Rotate borders.
        (s1, i1), (s2, i2), (s3, i3), (s4, i4) = CW_BORDERS_OF[side]
        for _ in range(3):
            self.cycle4((s4, i4), (s3, i3), (s2, i2), (s1, i1))
            i1, i2, i3, i4 = [(i + 1) % 8 for i in i1, i2, i3, i4]

    def move(self, move_id):
        side = move_id // 3
        rotation = move_id % 3
        if not rotation:
            self.cw(side)
        elif rotation == 1:
            self.half(side)
        else:
            self.ccw(side)
        self.history.add(move_id)

    def scramble(self):
        """100 non-redundant moves.
        
        20 moves can get to every possible config.
        """
        self.reset()
        while self.size() < 100:
            self.move(int(random() * 18))
        moves_made = self.get_history()
        self.clear_history()
        return moves_made
