"""This module contains constants for all other modules.

Jason Mahr
"""


## For history.py


"""Used when printing out a move history. Move indeces are 0 through 17
and correspond to this tuple.
"""
MOVES = ("L", "L2", "L'", "R", "R2", "R'", "F", "F2", "F'", "B", "B2", "B'",
         "U", "U2", "U'", "D", "D2", "D'")


## For cube.py


"""Constants for sides in the cube data structure.

For consistency, all functions taking these as arguments use the
variable name `side`.
"""
L, R, F, B, U, D = 0, 1, 2, 3, 4, 5


"""Constants for each tile. Format: L0 -> (0, 0); U3 -> (4, 3) = (U, 3).
The resulting tuple is the side then the index. Makes code much cleaner.

For consistency, all functions taking these as arguments either use the
variable name `tile` or deconstructs a tile into variables named `side`
and `index`.
"""
L0, L1, L2, L3, L4, L5, L6, L7 = map(lambda ind: (L, ind), range(8))
R0, R1, R2, R3, R4, R5, R6, R7 = map(lambda ind: (R, ind), range(8))
F0, F1, F2, F3, F4, F5, F6, F7 = map(lambda ind: (F, ind), range(8))
B0, B1, B2, B3, B4, B5, B6, B7 = map(lambda ind: (B, ind), range(8))
U0, U1, U2, U3, U4, U5, U6, U7 = map(lambda ind: (U, ind), range(8))
D0, D1, D2, D3, D4, D5, D6, D7 = map(lambda ind: (D, ind), range(8))


"""Constants for the lowest index of each side bordering the given side
given in clockwise order of bordering sides from the perspective of the
given side. Explained in much more detail in cube.py.
"""
CW_BORDERS_OF = ((F6, D6, B2, U6), (F2, U2, B6, D2), (L2, U4, R6, D0),
                 (L6, D4, R2, U0), (L0, B0, R0, F0), (L4, F4, R4, B4))


## For fitness.py


"""Convenience for checking colors. Use: if cube.get(L3) in LR:"""
LR = (L, R)
FB = (F, B)
UD = (U, D)


"""These weights were optimized for solution speed and length."""
G0_WEIGHT = 10
G1A_WEIGHT = 10
G1B_WEIGHT = 40
G2_WEIGHT_A = 16000
G2_WEIGHT_B = 800
G2_WEIGHT_C = 50
G3A_WEIGHT_A = 15
G3A_WEIGHT_B = 75
G3B_WEIGHT_A = 5
G3B_WEIGHT_B = 15
G3B_WEIGHT_C = 15
G3C_WEIGHT = 5


## For algorithm.py


"""Thistlethwaite Algorithm Moves and Phases."""
G0_MOVES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
G1_MOVES = (1, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
G2_MOVES = (1, 4, 7, 10, 12, 13, 14, 15, 16, 17)
G3A_MOVES = (1, 4, 7, 10, 13, 16)
G3B_MOVES = (7, 10, 13, 16)
G3C_MOVES = (13, 16)
MOVE_CHOICES = (G0_MOVES, G1_MOVES, G1_MOVES, G2_MOVES, G3A_MOVES, G3B_MOVES,
                G3C_MOVES)
NUM_MOVE_CHOICES = map(len, MOVE_CHOICES)
NUM_PHASES = len(MOVE_CHOICES)
MAX_NUM_MOVES = [8, 6, 14, 16, 10, 8, 2]
FITNESS_WEIGHT = 10
SIZE_WEIGHT = 19


"""Constants."""
POP_SIZE = 11700
NUM_SURVIVORS = 390
MAX_PHASE_2_GENERATIONS_BEFORE_RESET = 30
NUM_SELECTIONS = 100000
GEOMETRIC_SELECTION = True


## For app.py


"""Basics"""
MINWIDTH, MINHEIGHT = 590, 0
FONT = 'Comic Sans MS'
BASE_SIZE = 12
TAB = " " * 6


"""Step 1"""
COLORS = ('Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Pink',
          'White', 'Silver', 'Gray', 'Black', 'Brown')
DROPDOWN_WIDTH = max([len(i) for i in COLORS]) + 3
FULL = 100


"""Step 2 Colors: Background, emphasis, error."""
BKGD = 'White'
EMPH = 'Black'
ERROR = 'Red'


"""Step 2 Canvas.

Think of the 2D grid as having 9 rows of 12 columns, a 12 x 9 grid.
Using indeces starting at 0, the left face would correspond to indeces
(0, 3) through (2, 5). Next, the front face would correspond to (3, 3)
through (5, 5).

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
                      || 7 | D | 3 ||                P   P   P
                      || 6 | 5 | 4 ||                P   P   P 
                      |-------------|

Each tile is 40 by 40 pixels, and in between faces there is a break of 3
pixels. Thus, each tile slot can be encoded as pixels, or addresses, as
they are in ADDR. There is a 50 pixel margin on the left and top sides.

A lot of these tiles are empty; six of them (labeled) are used as a
color panel so the user can input their cube. These six have indeces
stored in `PANEL_INDS`. `INDS` refers to non-center tiles.
"""
WIDTH, HEIGHT = 540, 455
ADDR = ((50, 89), (90, 129), (130, 169), (173, 212), (213, 252), (253, 292),
        (296, 335), (336, 375), (376, 415), (419, 458), (459, 498), (499, 538))
CENTER_INDS = ((1, 4), (7, 4), (4, 4), (10, 4), (4, 1), (4, 7))
PANEL_INDS = ((9, 7), (9, 8), (10, 7), (10, 8), (11, 7), (11, 8))
INDS = (((0, 3), (1, 3), (2, 3), (2, 4), (2, 5), (1, 5), (0, 5), (0, 4)),
        ((6, 3), (7, 3), (8, 3), (8, 4), (8, 5), (7, 5), (6, 5), (6, 4)),
        ((3, 3), (4, 3), (5, 3), (5, 4), (5, 5), (4, 5), (3, 5), (3, 4)),
        ((9, 3), (10, 3), (11, 3), (11, 4), (11, 5), (10, 5), (9, 5), (9, 4)),
        ((3, 0), (4, 0), (5, 0), (5, 1), (5, 2), (4, 2), (3, 2), (3, 1)),
        ((3, 6), (4, 6), (5, 6), (5, 7), (5, 8), (4, 8), (3, 8), (3, 7)))


"""Addresses based on indices stored as ((x1, x2), (y1, y2))."""
CENTERS = [(ADDR[x], ADDR[y]) for x, y in CENTER_INDS]
TILES = [[(ADDR[x], ADDR[y]) for x, y in side] for side in INDS]
PANEL = [(ADDR[x], ADDR[y]) for x, y in PANEL_INDS]


"""Step 2 Labels."""
LABEL = ('Left', 'Right', 'Front', 'Back', 'Top', 'Bottom')
LABEL_XY = ((110, 153), (356, 153), (135, 312), (479, 153), (233, 30),
            (233, 435))
