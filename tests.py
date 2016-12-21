"""This module implements tests. These tests were used during development
as minor sanity checks.

Jason Mahr
"""


from constants import *
from cube import Cube
from fitness import *
from history import History
from validate import is_even, is_solved


## For history.py


h = History()
moves = [1, 5, 1, 9, 9, 8, 8, 12, 14, 15, 17, 12, 2, 3, 6, 5, 7, 7, 9, 10]
for move in moves:
    h.add(move)
assert h.get() == ["R'", 'B2', 'F2', 'U', "L'", 'R', 'F', "R'", "B'"]


## For cube.py


c = Cube()
for move in moves:
    c.move(move)
assert c.get_cube() == [[1, 1, 5, 4, 3, 1, 4, 4], [3, 3, 0, 4, 2, 3, 4, 0],
                        [3, 5, 0, 2, 1, 2, 4, 2], [5, 5, 2, 3, 0, 3, 1, 0],
                        [4, 2, 2, 5, 5, 0, 1, 4], [0, 1, 3, 1, 5, 0, 2, 5]]


## For fitness.py


assert [fitness[i](c) for i in range(7)] == [20, 90, 250, 49050, 615, 120, 195]


## For validation.py


v = ([1, 2, 0], True)
w = ([2, 1, 0], False)
x = ([3, 0, 1, 2], False)
y = ([2, 3, 0, 1], True)
z = ([2, 3, 4, 1, 0], False)
for permutation, even in (v, w, x, y, z):
    assert is_even(permutation) == even


## For the public. Paste scramble and solution here.


scramble = ["L'", "U'", "D2", "U", "L'", "R2", "L2", "B"]
solution = ["B'", "L'", "R2", "D2", "L"]
c.reset()
for move in scramble + solution:
    c.move(MOVES.index(move))
assert is_solved(c)
