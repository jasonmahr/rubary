"""This module implements the genetic algorithm.

Jason Mahr
"""


from constants import *
from cube import Cube
from fitness import fitness
from random import random
from time import clock


def mutate(cube, phase):
    """Mutates a cube given the current phase."""

    # Conduct a random number of random moves
    num_moves = int(random() * (MAX_NUM_MOVES[phase] + 1))
    for _ in range(num_moves):
        move_index = int(random() * NUM_MOVE_CHOICES[phase])
        cube.move(MOVE_CHOICES[phase][move_index])

    # Update cube's fitness and fitness score
    fit = fitness[phase](cube)
    cube.set_fitness(fit)
    cube.set_fitness_score(FITNESS_WEIGHT * fit + SIZE_WEIGHT * cube.size())


def create_population(cube):
    """Instantiate a population of cubes based on the specified cube."""
    population = [None] * POP_SIZE
    for i in range(POP_SIZE):
        population[i] = Cube()
        population[i].copy(cube)
    return population


def reset_population(population, cube):
    """Resets a population based on a cube, used for local optima."""
    for i in range(POP_SIZE):
        population[i].copy(cube)


def next_generation(population, phase, selector):
    """Mutates all cubes then selects based on fitness_score."""
    for cube in population:
        mutate(cube, phase)
    population.sort(key=lambda cube: cube.fitness_score)

    # Go to next phase if all survivors have solved the current phase
    go_to_next_phase = True
    for i in range(NUM_SURVIVORS):
        if population[i].get_fitness():
            go_to_next_phase = False
            break
    
    # Update population (unless algorithm is done) and return
    if not (phase == NUM_PHASES - 1 and go_to_next_phase):
        for i in range(NUM_SURVIVORS, POP_SIZE):
            population[i].copy(population[selector()])
    return go_to_next_phase


def solve(cube, selector, mailbox):
    """Solves a cube using the given selector. Sends progress updates to
    the provided mailbox, a callback function.
    """

    # Instantiate variables and start clock
    generations, resets, phase = 0, 0, 0
    population = create_population(cube)
    start = clock()

    # While algorithm is not complete
    while phase < NUM_PHASES:
        generations += 1
        if generations > MAX_PHASE_2_GENERATIONS_BEFORE_RESET and phase < 3:
            # Reset only necessary for the bottleneck of phase 2
            reset_population(population, cube)
            generations = 1
            phase = 0
            resets += 1

        # Populate next generation
        go_to_next_phase = next_generation(population, phase, selector)

        # Phase for the user should be 1-indexed instead of 0-indexed.
        mailbox(generations, phase + 1, population[NUM_SURVIVORS-1].fitness,
                clock() - start)

        if go_to_next_phase:
            phase += 1
    
    # Clean up and return
    time = clock() - start
    generations += resets * MAX_PHASE_2_GENERATIONS_BEFORE_RESET
    solution = population[0].get_history()
    return (time, generations, solution)
