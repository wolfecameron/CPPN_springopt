'''
This file contains all code for implementing CPPN using DEAP
CPPN implementation is recreated using creator in DEAP library
implementation details are same as other full CPPN files
'''
from deap import base
from deap import tools
from deap import algorithms
from deap import creator
from FULL_CPPN_struct import Genotype
from FULL_CPPN_deaphelp import weightMutate, conMutate, nodeMutate, xover
from FULL_CPPN_innovation import GlobalInnovation

'''
evaluation function for evolution
@param individual the organism that is being evaluated
@param sharingMatrix used for explicit fitness sharing
'''
def evaluate(pop, sharingMatrix):
	return 0

# create class for maximizing fitness and creating individual
creator.create("FitnessMax", base.Fitness, weights = (1.0,))
creator.create("Individual", Genotype, fitness = creator.FitnessMax)

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
NUM_IN = 2
NUM_OUT = 1
toolbox.register("individual", Genotype, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
POP_SIZE = 150
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n = POP_SIZE)

# register all functions needed for evolution in the toolbox
toolbox.register("mate", xover)
toolbox.register("weightMutate", weightMutate)
toolbox.register("connectionMutate", conMutate)
toolbox.register("nodeMutate", nodeMutate)


