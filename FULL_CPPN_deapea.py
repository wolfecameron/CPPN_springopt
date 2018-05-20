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
import numpy as np
from FULL_CPPN_evalg import getSharingMatrix, speciatePopulationFirstTime, speciatePopulationNotFirstTime
from FULL_CPPN_evalg import getFittestFromSpecies

'''
fitness evaluation used for DEAP CPPN implementation
@params individual the organism that is currently being evaluated
@sharingMatrix used for speciation and calculating niche count of an individual
@row the row of the sharingMatrix that corresponds to the current individual
@return fitness of individual in a tuple
'''
def evaluate(individual, sharingMatrix):
	# store inputs and actual/expected values in same order in lists 
	inputs = [[0,0], [1,0], [0,1], [1,1]]
	expectedOutputs = [0,1,1,0]
	actualOutputs = []
	# get output of individual for all different inputs
	for values in inputs:
		actualOutputs.append(individual.getOutput(values))
	fitness = 0.0
	# find niche count of first row and then delete first row
	nicheCount = np.sum(sharingMatrix[0])
	sharingMatrix = numpy.delete(sharingMatrix, (0), axis=0)
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i])**2)

	return (fitness/nicheCount),


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
toolbox.register("evaluate", evaluate)
toolbox.register("mate", xover)
toolbox.register("weightMutate", weightMutate)
toolbox.register("connectionMutate", conMutate)
toolbox.register("nodeMutate", nodeMutate)
toolbox.register("map", map)


'''
the main function for the DEAP evolutionary algorithm
the main EA loop is contained inside of this function
NOTE: pop size is set where the population function is registered
'''
def main(nGen, weightMutpb, conMutpb, thresh, alpha, theta1, theta2, theta3):
	pop = toolbox.population()
	for g in range(NGEN):
		sharingMatrix = getSharingMatrix(pop, threshold, alpha, theta1, theta2, theta3)
		fits = toolbox.map(toolbox.evaluate, pop, sharingMatrix)
		for ind,fit in zip(pop,fits):
			ind.fitness.values = fit
			ind.fitness = fit
		species = []
		if(g == 0):
			species = speciatePopulationFirstTime(pop, thresh, theta1, theta2, theta3)
		else:
			species = speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3)
		# fittest from species function selects all species representatives
		# and sets the species variable for the rest of the population to sys.maxsize
		fitTup = getFittestFromSpecies(species)
		bestInSpecies = fitTup[0]
		pop = fitTup[1]




# runs the main evolutionary loop if this file is ran from terminal
if __name__ == '__main__':
	main()
