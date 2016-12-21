"""Implementation of a Rank and a Geometric selector.

The Geometric selector performed better in tests.

Jason Mahr
"""


from constants import NUM_SELECTIONS, NUM_SURVIVORS
from random import random


class Rank:
    """A selector for restricted rank selection.
    
    Only the best NUM_SURVIVORS cubes can be selected from, and the
    fitness of the best cube is NUM_SURVIVORS, the fitness of the
    second-best cube NUM_SURVIVORS - 1, etc., and the fitness of the
    last survivor is 1.
    
    The restriction allows for controlled progression among phases. All
    cubes in a population need to have met a phase's requirements before
    proceeding to the next phase, so restriction is necessary otherwise
    this will never happen.

    Meanwhile, the rank selection is helpful because cubes' fitness
    scores can change drastically with a single move or phase
    transition, and thus a cube only slightly better or perhaps even
    worse may have a much better fitness with just a single move; rank
    selection is a standard way to account for this.

    For some intuition, the probability of selecting the best among 10
    is 10/55, then the next is 9/55, etc., and the last is 1/55.

    The selector generates NUM_SELECTIONS random indices before the
    algorithm starts to reduce computation time within the algorithm.
    """
    def __init__(self):
        
        # Calculate fitnesses
        self.fitnesses = [NUM_SURVIVORS - rank for rank in range(NUM_SURVIVORS)]

        # Cumulative fitnesses
        for i in range(1, NUM_SURVIVORS):
            self.fitnesses[i] += self.fitnesses[i - 1]
        self.sum = self.fitnesses[i - 1]

        # Compile NUM_SELECTIONS selections
        self.selections = [self.select() for _ in range(NUM_SELECTIONS)]

        # Index
        self.index = -1

    def select(self):
        """Selects a survivor based on rank selection and returns its
        index.
        """
        target = int(random() * self.sum)
        for i in range(NUM_SURVIVORS):
            if target < self.fitnesses[i]:
                return i
    
    def __call__(self):
        """There is a clear behavior for this class."""
        self.index = (self.index + 1) % NUM_SELECTIONS
        return self.selections[self.index]
    

class Geometric:
    """A similar selector except probability is distributed more evenly.
    The generation of values was derived from mathematical properties of
    geometric series. The complicated math had to be used, otherwise
    there would be an integer overflow calculating powers like
    NUM_SURVIVORS ** (NUM_SURVIVORS - 1).

    Intuitively, let ratio = (NUM_SURVIVORS - 1.) / NUM_SURVIVORS. Then
    the probability of picking the second element is ratio * the
    probability of picking the first element, and this pattern continues
    down through all elements.

    The structure of this class is similar to that of the Rank class.
    """
    def __init__(self):
        
        # Calculate cumulative fitnesses
        ratio = (NUM_SURVIVORS - 1.) / NUM_SURVIVORS
        prob = (1. / NUM_SURVIVORS) / (1 - ratio ** NUM_SURVIVORS)
        self.fitnesses = [None] * NUM_SURVIVORS
        self.fitnesses[0] = prob
        self.fitnesses[NUM_SURVIVORS - 1] = 1
        for i in range(1, NUM_SURVIVORS - 1):
            prob *= ratio
            self.fitnesses[i] = self.fitnesses[i - 1] + prob

        # Same as above
        self.selections = [self.select() for _ in range(NUM_SELECTIONS)]
        self.index = -1

    def select(self):
        # Since probabilities are from 0 to 1, no need for a sum
        target = random()
        for i in range(NUM_SURVIVORS):
            if target < self.fitnesses[i]:
                return i
    
    def __call__(self):
        self.index = (self.index + 1) % NUM_SELECTIONS
        return self.selections[self.index]
