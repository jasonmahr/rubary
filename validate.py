"""Checks validity of cubes and whether they are solved.

These just get() information from cubes without making any changes.

Jason Mahr
"""


from constants import *
from fitness import edge_flipped_correctly, miscolored_tiles


def is_solved(cube):
    return not miscolored_tiles(cube)


def is_even(permutation):
    """This is a mathematical function. It takes a list of n numbers
    0, 1, . . ., n - 1 in any permutation and then returns whether that
    permutation is even. Even means an even number of swaps results in
    the given configuration from ordered set. 1 2 0 is even; 2 1 0 odd.

    Citation: Help in thinking about permutations from Wikipedia:
    https://en.wikipedia.org/wiki/Parity_of_a_permutation.
    """
    n = len(permutation)
    visited = [None] * n
    for m in permutation:
        if not 0 <= m < n:
            return False
        visited[m] = False
    if None in visited:
        # Permutation did not have the values 0, 1, . . ., n - 1
        return False

    """There must be an even number of odd cycles. This is tracked by
    flipping `is_even` for each member of a cycle. That way, odd cycles
    will flip `is_even`, meaning an odd number of odd cycles, which
    means the permutation is odd, will result in `is_even` being False.

    Each cycle is only examined once. This is achieved by keeping track
    of visited entries in the `visited` array.
    """
    is_even = True
    for m in permutation:
        if not visited[m]:
            p = permutation[m]
            while p != m:
                is_even = not is_even
                visited[p] = True
                p = permutation[p]
    return is_even


def not_color(color):
    """Checks if an integer is a valid color. Quite superfluous due to
    the hard invariant in the code that maintains color validity, but
    just to be safe.
    """
    return not 0 <= color <= 5
    

def is_valid(cube):
    """Checks that a cube is solvable.

    Citation: Rules from (https://ruwix.com/the-rubiks-cube/
                          unsolvable-rubiks-cube-invalid-scramble/)

    This is important: only 1/12 cubes are solvable (this is among
    cubes with one of each tile and corner tiles in plausible
    orientations). For example, a cube with a single edge flipped
    clearly cannot be solved. (Two edges can though, as edges must have
    an even parity).
    
    Checking for validity helps prevent cycling forever for incorrectly
    inputted cubes, and also prevents the user from having to re-input
    an entire cube due to one mistake. 

    The function first checks edge parity and corner parity, both times
    multitasking by recording useful permutation information. If both
    have parities of 0, the third requirement is verified, which is that
    the order of pieces on the cube with respect to the start state must
    be an even permutation.
    """
    
    ## Edges

    """There are 12 edges.
            LF,  LU,  LB,  LD;  RF,  RU,  RB,  RD;  FU,  FD;  BU,  BD.
    Their color combinations are:
            02,  03,  04,  05;  12,  13,  14,  15;  24,  25;  34,  35.
    The sums of cubes is unique. They are:
             8,  27,  64, 125;   9,  28,  65, 126;  72, 133;  91, 152.
    (Note that the sum of squares for both 05 and 34 is 25.)
    
    So we can use sums of cubes to unique identify the edges. There
    should be exactly one of each in a cube. The purpose of using sums
    of cubes is that this eliminates the hassle of checking for both
    (0, 2), and (2, 0) as the same thing.
    
    `edge_pos` encodes positions (!). `edge_colors` encodes colors in
    the form of the unique sums of cubes.

    Furthermore, the values corresponding to `edge_colors` is a permutation
    of the values corresponding to `edge_pos`. This permutation is
    recorded as edge_permutation. It needs to be such that corner and
    edge permutation together is even, which means either both are even
    or both are odd.

    The position of values in `edge_permutation` corresponds to the
    order of `edge_colors`, while the values correspond to the indices
    of `edge_pos`. Essentially, if edge_permutation[0] = 1, it means
    that for the 0th color combination in `edge_color`, which is the
    left color and the front color, the one edge with these two colors
    is located at the 1st edge position in `edge_pos`, which is on the
    left and up edges.

    The order in `edge_pos` is the same as in the first line of this
    comment. Some edges are flipped with respect to provided in the
    first line of this comment, and this is so that the helper function
    edge_flipped_correctly from `fitness.py` can be reused.

    As for edge parity: Essentially, phase 0 takes the cube to a place
    where no edges are misflipped. The number of misflipped edges is
    always even. If it is odd, the cube is invalid. (If you start from a
    new cube and flip one edge, clearly this cube is not solvable.) So,
    this must be checked for, and it is checked for similarly to in
    `is_even`, where a bool is flipped every time there is a misflipped
    edge.
    """
    edge_pos = ((L3, F7), (U7, L1), (L7, B3), (D7, L5), (R7, F3), (U3, R1),
                (R3, B7), (D3, R5), (U5, F1), (D1, F5), (U1, B1), (D5, B5))
    edge_colors = (8, 27, 64, 125, 9, 28, 65, 126, 72, 133, 91, 152)
    edge_permutation = [None] * 12
    edge_parity_is_even = True

    # Iterate over edge positions
    for edge_position_index, edge_position in enumerate(edge_pos):
        
        # Get the colors
        edge_0 = cube.get(edge_position[0])
        edge_1 = cube.get(edge_position[1])

        # Check this edge has colors between 0 and 5
        if not_color(edge_0) or not_color(edge_1):
            return False

        # Check the two colors of this edge are not the same or opposite
        if edge_0 // 2 == edge_1 // 2:
            return False

        # Sum of cubes uniquely indicates which colors are at position
        edge_color = edge_0 ** 3 + edge_1 ** 3

        """Get index of the `edge_color` within `edge_colors`. Note the
        color will definitely be in the list if the two values are
        between 0 and 5 and are not the same when integer-divided by 2.
        """
        edge_color_index = edge_colors.index(edge_color)

        # Check another edge position did not already have these colors
        if edge_permutation[edge_color_index] is not None:
            return False

        # Track the index in `edge_permutation`
        edge_permutation[edge_color_index] = edge_position_index

        # Flip `edge_parity` if this edge is misflipped
        if not edge_flipped_correctly(edge_0, edge_1):
            edge_parity_is_even = not edge_parity_is_even

    # Edge parity must be even
    if not edge_parity_is_even:
        return False

    ## Corners

    """In many respects, similar to edges. There are two aspects, parity
    and permutation.

    Corner parity can be 0, 1, or 2. Every clockwise turn of a corner
    increases the parity by 1 (which means a counterclockwise turn = two
    clockwise turns increases the parity by 2).

    There are 8 corners.
            UBR, UFL, DFR, DBL, UBL, UFR, DFL, DBR.
    
    For any of these corners, half of possible configurations of colors
    are invalid. Consider UFL. The colors can be U on the up side, F on
    the front side, and L on the left side. They can also be LUF (parity
    of 1) or FLU (parity of 2). However, they cannot be ULF. The only
    way to get ULF is to swap the L and F stickers from the corner
    piece. LFU and FUL are also invalid. So to save work we don't
    calculate a sum of cubes. Instead we start with UFL, rotating based
    on the location of the UD color (and recording parity) and then
    checking for existence in corner_colors.

    Notice that the U2, U6, D2, D6 corners have the FB faces second,
    whereas the other four have the LR faces second. This is because
    these corners form two different orbits. Consider a turn of U. Then
    F is on the R face and L is on the F face. Similarly, a turn of U'
    results in F being on the L face and R being on the F face. This is
    why FB and LR are swapped in the bottom half of the color arrays.

    Either way, if the UD color is on the UD sides, this is our
    reference point for a parity of 0. Only single turns of the LRFB
    faces will break this condition, resulting in nonzero parity. If UD
    is on the second face (FB for the UFL orbit and LR for the UFR
    orbit), then that increases parity by 1. Turning UFL clockwise
    places U on F and turning UFR clockwise places U on R. Finally, if
    UD is on the third face, this increases parity by 2.

    The code records parity optimistically, since if the corner is later
    deemed invalid, it just returns False. The code then checks whether
    the corner is valid by seeing if its parity-0 rotation is in
    corner_colors. This eliminates totally inplausible corners like
    LLL, and also the sticker-swapped arrangements like ULF, where L is
    on the second face (FB for UFL orbit; LR for UFR orbit).

    If the corner exists and another corner has not already claimed the
    same colors (cube would be invalid), permutation is recorded similar
    to with edges and is checked together with edges at the end.
    """
    corner_pos = ((U2, B0, R2), (U6, F0, L2), (D2, F4, R6), (D6, B4, L6),
                  (U0, L0, B2), (U4, R0, F2), (D0, L4, F6), (D4, R4, B6))
    corner_colors = ((U, B, R), (U, F, L), (D, F, R), (D, B, L),
                     (U, L, B), (U, R, F), (D, L, F), (D, R, B))
    corner_permutation = [None] * 8
    corner_parity = 0

    # Iterate over corner positions
    for corner_position_index, corner_position in enumerate(corner_pos):
        
        # Get colors. corner_#: corner such that if UD there, parity #.
        corner_0 = cube.get(corner_position[0])
        corner_1 = cube.get(corner_position[1])
        corner_2 = cube.get(corner_position[2])

        # Optimistically update parity while getting parity-0 of corner
        if corner_0 in (U, D):
            corner = (corner_0, corner_1, corner_2)
        elif corner_1 in (U, D):
            corner = (corner_1, corner_2, corner_0)
            corner_parity += 1
        elif corner_2 in (U, D):
            corner = (corner_2, corner_0, corner_1)
            corner_parity += 2
        else:
            return False
        
        # Find corner. If does not exist, stickers could be swapped.
        try:
            corner_color_index = corner_colors.index(corner)
        except ValueError:
            return False

        # Check another corner position didn't already have these colors
        if corner_permutation[corner_color_index] is not None:
            return False
        
        # Track the index in `corner_permutation`
        corner_permutation[corner_color_index] = corner_position_index

    # Corner parity must be 0
    if corner_parity % 3:
        return False

    ## Permutation
    
    """Edges and corners both have correct parities. Only one in 6 cubes
    with the correct tiles have correct parities (2 * 3 = 6).

    The technical rule for permutations is that the pieces among the
    whole cube must be an even permutation, but this can be split to
    separate corner and edge permutations, since a corner piece can't
    swap with an edge piece. This has simplified the function. For the
    overall permutation to be even, either both must be even, or both
    must be odd (Recall from is_even that two odd cycles is an even
    permutation. By the same logic, so are two odd permutations.) 
    """
    return is_even(corner_permutation) == is_even(edge_permutation)
