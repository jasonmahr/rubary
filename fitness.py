"""This module implements fitness functions for cubes.

The structure of the code is helper functions for each stage followed
by the main fitness scorer for that stage, named stage_fitness. Stages
are in order.

Please refer to Sections 2 and 4 of the paper for more details on any of
these functions.

In all fitness functions, a lower score is better.

Jason Mahr
"""


from constants import *


def edge_flipped_correctly(color_1, color_2):
    return color_1 not in FB and color_2 not in UD


def misoriented_edges(cube):
    """Goal: orient edges. Returns the number of wrongly flipped edges.
    This is described in Section 2.2 of the paper. The edges in `edges`
    are listed such that the first tile cannot be FB (U, D, and LR
    bordering FB) and the second tile cannot be UD (F, B, and LR
    bordering UD).
    """
    score = 12
    edges = ((L3, F7), (R7, F3), (L7, B3), (R3, B7), (U7, L1), (U3, R1),
             (U5, F1), (D7, L5), (D3, R5), (U1, B1), (D1, F5), (D5, B5))
    for edge in edges:
        score -= edge_flipped_correctly(cube.get(edge[0]), cube.get(edge[1]))
    return score


def g0_fitness(cube):
    return G0_WEIGHT * misoriented_edges(cube)


def misplaced_middle_edges(cube):
    """Goal: all middle edges should be in the middle layer. Since all
    edges are now oriented correctly, the LR middle edge tiles cannot be
    FB. If they are LR, this means that a middle edge is there. If it
    were a LR/UD edge, then the UD side would be on FB, a violation of
    G0. If they are UD, this means that the middle edge is not there,
    since middle edges do not have UD. Thus the LR tile of a middle edge
    position shows LR if and only if the tile there it is a middle edge.
    Thus, we just check L3, L7, R7, and R3.

    As described in the paper, there is a credit for having 2 wrong
    middle edges, since it is easier to resolve two wrong edges than
    one, for which another edge must first be made incorrect. The credit
    is granted by every other number of wrong edges being multiplied by
    3 (0 would still give a score of 0) so that 1 wrong edge has the
    higher score of 3.

    Also, there is a further bonus if the two correct edges are both on
    the front or both on the back, and furthermore the two missing edges
    are on U and D's border with the F/B face that the correct edges are
    not on. For instance, say the middle edges are at LB, RB (correct),
    UF, and DF. Then a single turn of the F face resolves the edges. So
    there is a further benefit for this arrangement.

    The arrangment is identified by having the edges tuple ordered
    with F and B sides alternating. That way, if the two middle edge
    positions missing middle edges are both on the F or B side, then
    their summed index would be even. However, if this is not the case,
    then the summed index is odd, and the algorithm returns 2, the bonus
    for just having two wrong edges.

    If this is the case, and additionally it is also the case that the
    two missing middle edges are on the U and D borders with the other
    F/B face, then the algorithm returns 1.
    """
    score = 0
    wrong_indeces_sum = 0
    for index, edge in enumerate((L3, L7, R7, R3)):
        if cube.get(edge) in UD:
            score += 1
            wrong_indeces_sum += index
    if score != 2:
        return score * 3

    if wrong_indeces_sum % 2:
        return 2

    # Return 1 or 2 depending on the harder criterion
    return 1 if (cube.get((U, 6 - wrong_indeces_sum)) in LR and
                 cube.get((D, wrong_indeces_sum)) in LR) else 2


def g1a_fitness(cube):
    return G1A_WEIGHT * misplaced_middle_edges(cube)


def misoriented_corners(cube):
    """Goal: rotate corners so that UD is showing on all UD corners.
    As mentioned in the paper, there is credit granted for specific
    formations within corner circuits both being UD.
    
    However this credit cannot matter if there are not at least 2
    misoriented corners, hence the early return if `score` < 2. The max
    deduction is 4, since there are only 8 corners (4 pairs).
    """
    score = 0
    for corner in (U0, U2, U4, U6, D0, D2, D4, D6):
        if cube.get(corner) not in UD:
            score += 1
    if score < 2:
        return score
    corner_pairs = ((R0, B6), (R2, F4), (R4, F2), (R6, B0),
                    (L0, F6), (L2, B4), (L4, B2), (L6, F0))
    for (corner1, corner2) in corner_pairs:
        if cube.get(corner1) in UD and cube.get(corner2) in UD:
            score -= 1
    return score


def g1b_fitness(cube):
    return g1a_fitness(cube) + G1B_WEIGHT * misoriented_corners(cube)


def uniform_top_corners(cube):
    """Goal: Get all U corners or all D corners on U to enable checking
    for correct corner circuits. Outputs the number of turns until this
    is achieved.

    `u_on_u` tracks how many U tiles are on U. If it is 0 or 4, the
    function returns 0.
    """
    u_on_u = 0

    # Only used if there is only one such corner
    u_index = None
    d_index = None

    for index in (0, 2, 4, 6):
        if cube.get((U, index)) == U:
            u_on_u += 1
            u_index = index
        else:
            d_index = index

    if u_on_u in (0, 4):
        return 0

    """If `u_on_u` is 1, then u_index will have the index of the corner
    on U with U. There is a corner on D with just D. If that corner is
    not directly below or opposite, just do a half turn to bring a U to
    the top (it will be next to the U on the top), then rotate the top,
    then do another half turn to solve. So there are 3 moves needed. If
    the corner is directly below or opposite, there needs to be one D
    turn first to get it to not directly below or opposite, hence 4. The
    corners not directly below or opposite are the ones that have the
    same index and the same index +/- 4. This is checked by first
    modding by 4 and then adding 4.

    The logic is the same if `u_on_u` is 3, except with U and D
    reversed.
    """
    if u_on_u == 1:
        u_index %= 4
        if D in (cube.get((D, u_index)), cube.get((D, u_index + 4))):
            return 3
        return 4

    if u_on_u == 3:
        d_index %= 4
        if U in (cube.get((D, d_index)), cube.get((D, d_index + 4))):
            return 3
        return 4

    """If `u_on_u` is 2, then U and D both have two Us and two Ds. If
    they both have these arranged diagonally, it takes 3 turns if the
    same colors are on top of each other (half turn of LRFB, half turn
    of UD, half turn of LRFB). Otherwise it takes 4, first a U to get
    the same colors on top of each other. On top means they would
    intersect from a bird's eye view looking down on the top side.

    If only one is diagonal, five turns are needed.

    If neither is diagonal, then only one LRFB half turn is needed if no
    same colors are on top of each other, else two turns are needed,
    the first turn to get to the position with no same colors on top of
    each other.
    """
    u_color_pairs_diagonal = cube.get(U0) == cube.get(U4)
    d_color_pairs_diagonal = cube.get(D0) == cube.get(D4)

    if u_color_pairs_diagonal and d_color_pairs_diagonal:
        return 3 if cube.get(U0) == cube.get(D6) else 4
    if u_color_pairs_diagonal or d_color_pairs_diagonal:
        return 5
    if cube.get(U0) == cube.get(D2) and cube.get(U2) == cube.get(D0):
        return 1
    return 2


def corner_pairs(cube):
    """Goal: Pairs of corners around the top and bottom rows of LRFB
    should either all match or all mismatch. If one of the two goals is
    closer, returns the number of pairs that do not conform, with a
    credit for each side where both pairs do not conform. If exactly
    four pairs mismatch, returns the lesser score.

    In calculating score, the number of nonconforming pairs is
    multiplied by 4 and the number of credits is multiplied by 5. This
    credit ratio works well, and using whole numbers avoid floats.
    
    Also, this checks for corner color as well. Usually mistakes here
    can just be fixed by quarter U or D turns. Thus pairs matching or
    mismatching is the priority. It suffices to verify that two L
    corners in separate rows are both in LR, as this would mean the R
    corners are also in LR, and so the FB corners would be in FB. So,
    if all corner pairs conform, the function returns the number of
    non LR colors at (L3, L7), i.e., 0, 1, or 2, all less than 4,
    another reason for the multiple.
    """
    score = 0
    sides_both_pairs_matching = 0
    sides_both_pairs_mismatching = 0

    for side in (L, R, F, B):
        mismatching_this_side = ((cube.get((side, 0)) != cube.get((side, 2))) +
                                 (cube.get((side, 4)) != cube.get((side, 6))))
        if not mismatching_this_side:
            sides_both_pairs_matching += 1
        else:
            score += mismatching_this_side
            if mismatching_this_side == 2:
                sides_both_pairs_mismatching += 1
    
    if score in (0, 8):
        return (cube.get(L0) not in LR) + (cube.get(L4) not in LR)
    
    score *= 4
    sides_both_pairs_matching *= 5
    sides_both_pairs_mismatching *= 5

    # Return based on the closer goal
    if score < 16:
        return score - sides_both_pairs_mismatching
    if score > 16:
        return 32 - score - sides_both_pairs_matching
    return 16 - max(sides_both_pairs_matching, sides_both_pairs_mismatching)

    
def edge_colors(cube):
    """Goal: Top and bottom edges of the LR and FB faces ought to be LR
    and FB, respectively. Like several other functions, improves by
    returning the number of turns needed until the function is
    satisfied, not just the number of incorrect tiles.

    There must be an even number of edges wrong, and there can be at
    most four wrong in each circuit. The circuit counts are commutable.
    Here is a chart of the number wrong:

    Sum   c0    c1    Moves SS    Rationale
        
    0     0     0     0     0     Solved state
    4     4     0     4     16    d' l2 r2 u (base)
          3     1     5     10    l2 brings c1's 1 into c0, then base
          2     2     6     8     l2 r2 brings c1's 2 into c0, base
    8     4     4     6     32    d' l2 r2 f2 b2 d'
    2     1     1     9     2     base converts c0's 1 to 3, then 3-1
          2     0    10     4     l2 for 1-1, then 1-1
    6     3     3     9     18    base converts c1's 3 to 1, then 3-1
          4     2    10     20    l2 then 3-3 (1 + 9 moves = 10 moves)

    SS, the sums of the squared values of c0 and c1, are unique, so
    using this avoids having to deal with the commutation.
    """
    circuit0_wrong = ((cube.get(L1) not in LR) + (cube.get(R1) not in LR) +
                      (cube.get(F5) not in FB) + (cube.get(B5) not in FB))
    circuit1_wrong = ((cube.get(L5) not in LR) + (cube.get(R5) not in LR) +
                      (cube.get(F1) not in FB) + (cube.get(B1) not in FB))

    sum_of_squares = circuit0_wrong ** 2 + circuit1_wrong ** 2
    lookup = ((0, 0), (16, 4), (10, 5), (8, 6), (32, 6), (2, 9), (4, 10),
              (18, 9), (20, 10))
    
    for sum, moves in lookup:
        if sum_of_squares == sum:
            return moves

    # This would not happen in a real run, just for the sake of tests
    return 100000


def g2_fitness(cube):
    return (G2_WEIGHT_A * uniform_top_corners(cube) +
            G2_WEIGHT_B * corner_pairs(cube) +
            G2_WEIGHT_C * edge_colors(cube))


def fbud_edges(cube):
    """Goal: The 8 edge tiles on FBUD bordering LR must be the correct
    color. This is because if the LF and LB edge pieces were swapped,
    this could not be resolved without L2 or R2. U2 and D2 would not
    touch these edges, and F2 and B2 would keep them on the wrong FB
    side.

    Since we are in G3, an edge tile on F will either have the color F
    or B. Since that is the case, if both tiles on F are F, then the
    ones on the back must be B, so we only have to check two sides.
    """
    return ((cube.get(F3) != F) + (cube.get(F7) != F) + (cube.get(U3) != U) +
            (cube.get(U7) != U))


def uniform_top(cube, side):
    """True if top row of given side of given cube is uniform."""
    return cube.get((side, 0)) == cube.get((side, 1)) == cube.get((side, 2))


def uniform_bottom(cube, side):
    """True if bottom row of given side of given cube is uniform."""
    return cube.get((side, 4)) == cube.get((side, 5)) == cube.get((side, 6))


def fbud_rows(cube):
    """Goal: The tiles not considered in the above function must be
    uniform in their rows. This is because there is no way to break
    apart these rows without turning the L or R sides.
    """
    score = 8
    for side in (F, B, U, D):
        score -= (uniform_top(cube, side)) + (uniform_bottom(cube, side))
    return score


def g3a_fitness(cube):
    return G3A_WEIGHT_A * fbud_edges(cube) + G3A_WEIGHT_B * fbud_rows(cube)


def ud_tiles(cube):
    """Goal: U and D must be fully solved, since U2 and D2 do not change
    the tiles on U and D. D is fully solved if U is fully solved due to
    opposite colors, so only one side needs to be checked.
    """
    score = 0
    for index in range(8):
        score += (cube.get((U, index)) != U)
    return score


def lr_edges(cube):
    """Goal: Middle edges must be solved, since UD turns do not affect
    these. As with before, checking one side is sufficient due to
    opposite colors.
    """
    return (cube.get(L3) != L) + (cube.get(L7) != L)


def lr_rows(cube):
    """Goal: The tiles not considered in the above function must be
    uniform in their rows, since UD turns cannot break these rows up.
    """
    return 4 - (uniform_top(cube, L) + uniform_bottom(cube, L) +
                uniform_top(cube, R) + uniform_bottom(cube, R))


def g3b_fitness(cube):
    return (G3B_WEIGHT_A * ud_tiles(cube) + G3B_WEIGHT_B * lr_edges(cube) +
            G3B_WEIGHT_C * lr_rows(cube))


def miscolored_tiles(cube):
    """Returns the number of miscolored tiles."""
    score = 0
    for i in range(8):
        score += ((cube.get((L, i)) != L) + (cube.get((R, i)) != R) +
                  (cube.get((F, i)) != F) + (cube.get((B, i)) != B) +
                  (cube.get((U, i)) != U) + (cube.get((D, i)) != D))
    return score


def g3c_fitness(cube):
    """num_errors() also used elsewhere."""
    return G3C_WEIGHT * miscolored_tiles(cube)


"""Easy access to fitness functions based on current phase."""
fitness = [g0_fitness, g1a_fitness, g1b_fitness, g2_fitness, g3a_fitness,
           g3b_fitness, g3c_fitness]
