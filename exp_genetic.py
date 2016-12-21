"""Experiment. Algorithm rarely converges, as discussed in paper.

Jason Mahr
"""


from constants import *
from cube import Cube
from fitness import *
from algorithm import *
from time import clock


MUTATION_RATE = .01
CROSSOVER_RATE = .7


class Gene:
    def __init__(self, gene):
        self.gene = gene
        self.fit = 0
        self.fitness = 0
    def copy(self, other):
        self.gene[:] = other.gene


def eval(gene, cube, phase):
    c = Cube()
    c.copy(cube)
    moves = dedup(gene.gene)
    for move in moves:
        c.move(move)
    fit = fitness[phase](c)
    gene.fit = fit
    gene.fitness = FITNESS_WEIGHT * fit + SIZE_WEIGHT * len(moves)


def dedup(gene):
    return gene


def new_allele(phase):
    return MOVE_CHOICES[phase][int(random() * NUM_MOVE_CHOICES[phase])]


def new_gene(length, phase):
    return Gene([new_allele(phase) for _ in range(length)])


def mutate(gene, phase):
    for i in range(len(gene.gene)):
        if random() < MUTATION_RATE:
            gene.gene[i] = new_allele(phase)


def crossover(gene1, gene2, phase):
    position = 0
    if random() < CROSSOVER_RATE:
        position = int(random() * len(gene1.gene))
    gene = Gene(gene1.gene[:position] + gene2.gene[position:])
    mutate(gene, phase)
    return gene
    

def create_population(phase):
    return [new_gene(LIMIT_NUM_MOVES[phase], phase) for _ in range(POP_SIZE)]


def reset_population(population, phase):
    population = create_population(phase)


def next_generation(population, cube, phase, selector):
    for gene in population:
        eval(gene, cube, phase)

    population.sort(key=lambda gene: gene.fitness)

    go_to_next_phase = True
    for i in range(NUM_SURVIVORS):
        if population[i].fit:
            go_to_next_phase = False
    print population[0].fit

    if not (phase == NUM_PHASES - 1 and go_to_next_phase):
        for i in range(NUM_SURVIVORS, POP_SIZE):
            population[i] = crossover(population[selector.next()],
                                      population[selector.next()], phase)
    
    if go_to_next_phase:
        return population[0]


def solve(cube, selector):
    time = clock()

    genes = [None] * 7
    cubes = [cube] * 7

    generations = 0
    resets = 0
    phase = 0

    population = create_population(phase)

    while phase < NUM_PHASES:
        generations += 1
        print ('We are on generation ' + str(generations) + ', phase ' +
               str(phase+1) + ', time so far ' +
               str(clock() - time)
        
        if generations > MAX_GENERATIONS_BEFORE_RESET:
            phase = 0
            reset_population(population, phase)
            generations = 0
            resets += 1
        else:
            gene = next_generation(population, cubes[phase], phase, selector)
            if gene:
                genes[phase] = gene.gene
                phase += 1
                if phase < NUM_PHASES:
                    c = Cube()
                    c.copy(cubes[phase - 1])
                    for move in gene.gene:
                        c.move(move)
                    cubes[phase] = c
                    for g in population:
                        g.copy(gene)
    
    time = clock() - time
    total_generations = resets * MAX_GENERATIONS_BEFORE_RESET + generations
    flattened_genes = [j for i in x for j in i]

    return (time, total_generations, flattened_genes)
    

def main():   
    c = Cube()
    c.reset()
    for move in [7, 1, 3, 9, 5, 12, 14, 17, 1, 15, 13, 2, 8, 7, 16, 10, 9, 11, 
                 4, 14, 1, 6]:
        c.move(move)

    selector = Selector2()
    solution = solve(c, selector)
    print (str(solution[1]) + '\t' + str(solution[0].seconds))
    print solution[2]
    

g = Gene([7, 1, 3, 9, 5, 12, 14, 17, 1, 15, 13, 2, 8, 7, 16, 10, 9, 11, 4, 14,
          1, 6])
new_cube = Cube()
new_cube.reset()
for phase in range(7):
    eval(g, new_cube, phase)
    print g.fit


main()
