'''Creates all configuration that is used for DEAP in CPPN experiments'''

from deap import base, tools, algorithms, creator
from scoop import futures
import pickle

from FULL_CPPN_struct import Genotype
from FULL_CPPN_deaphelp import weightMutate, conMutate, nodeMutate, xover, actMutate
from FULL_CPPN_evaluation import evaluate_pic_scoop, evaluate_nov_pic

"""The below contains all of the deap configuration used for CPPN so that it can be
called and edited from a central location"""

# constants used for deap configuration
weights=(-1.0, -1.0)
NUM_IN=2
NUM_OUT=1
POP_SIZE=100

#create types needed for deap
creator.create("FitnessMulti", base.Fitness, weights=weights)
creator.create("Individual", Genotype, fitness=creator.FitnessMulti)

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
toolbox.register("individual", creator.Individual, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=POP_SIZE)

# register all functions needed for evolution in the toolbox
toolbox.register("evaluate", evaluate_pic_scoop)
toolbox.register("assign_fit", evaluate_nov_pic)
toolbox.register("select", tools.selNSGA2, k=POP_SIZE)
toolbox.register("mate", xover)
toolbox.register("weightMutate", weightMutate)
toolbox.register("connectionMutate", conMutate)
toolbox.register("nodeMutate", nodeMutate)
toolbox.register("activationMutate", actMutate)
toolbox.register("map", futures.map)


def get_tb():
	"""method to get the toolbox object that is needed for
	evolution - the toolbox is configured in this file so that
	the configuration is central"""

	return toolbox
	
