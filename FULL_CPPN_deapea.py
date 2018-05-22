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
from FULL_CPPN_evalg import getFittestFromSpecies, getNicheCounts
from FULL_CPPN_vis import visConnections, visHiddenNodes
import random as r
import sys

'''
fitness evaluation used for DEAP CPPN implementation
@params individual the organism that is currently being evaluated
@param nicheCounts used to find the sharing percentage of an individual for explicit fitness sharing
@row the row of the sharingMatrix that corresponds to the current individual
@return fitness of individual in a tuple
'''
def evaluate(individual, nicheCounts, row):
	# store inputs and actual/expected values in same order in lists 
	inputs = [[0,0], [1,0], [0,1], [1,1]]
	expectedOutputs = [0,1,1,0]
	actualOutputs = []
	# get output of individual for all different inputs
	for values in inputs:
		actualOutputs.append(individual.getOutput(values)[0])
	fitness = 0.0
	# find niche count of first row and then delete first row
	nicheCount = nicheCounts[row]
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i])**2)
	# square the resulting fitness	
	fitness = fitness**2

	return (fitness/nicheCount),


# create class for maximizing fitness and creating individual
# must name fitness atribute fit_obj because fitness is a instance variable of Genotype class
creator.create("FitnessMax", base.Fitness, weights = (1.0,))
creator.create("Individual", Genotype, fit_obj = creator.FitnessMax) 

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
NUM_IN = 2
NUM_OUT = 1
toolbox.register("individual", creator.Individual, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
POP_SIZE = 150
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n = POP_SIZE)

# register all functions needed for evolution in the toolbox
TOURN_SIZE = 2
toolbox.register("evaluate", evaluate)
toolbox.register("select", tools.selTournament, k = 1, tournsize = TOURN_SIZE, fit_attr = "fit_obj")
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
def main(nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, thresh, alpha, theta1, theta2, theta3, numIn, numOut):
	pop = toolbox.population()
	# use global innovation object to track the creation of new innovation numbers during evolution
	gb = GlobalInnovation(numIn, numOut)
	for g in range(NGEN):
		print("RUNNING GENERATION " + str(g))
		# create sharing matrix to use to calculate niche count
		print("*making sharing matrix")
		print(len(pop))
		if(g == 35):
			visConnections(pop)
			visHiddenNodes(pop)

		nicheCounts = getNicheCounts(getSharingMatrix(pop, thresh, alpha, theta1, theta2, theta3))
		fits = []
		# use row counter as the correct index into the sharing matrix for fitness calculation
		# find all fitness values for individuals in population
		print("*getting fitness")
		row = 0 
		for ind in pop:
			fits.append(toolbox.evaluate(ind, nicheCounts, row))
			row += 1

		# assign all the fitness values to the individuals
		# NOTE: each elements of fits will be a tuple	
		for ind,fit in zip(pop,fits):
			ind.fit_obj.values = fit
			ind.fitness = fit[0]
		
		# speciate the population after finding corresponding fitnesses
		print("*creating species")
		species = []
		if(g == 0):
			species = speciatePopulationFirstTime(pop, thresh, theta1, theta2, theta3)
		else:
			species = speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3)
		print(len(species))
		#input()
		
		# fittest from species function selects all species representatives
		# and sets the species variable for the rest of the population to sys.maxsize
		fitTup = getFittestFromSpecies(species)
		bestInSpecies = fitTup[0]
		print(len(bestInSpecies))
		#input("Looking at the number of individuals directly selected")
		pop = fitTup[1]
		print("*selecting new population")
		pop = toolbox.select(pop, k = len(pop))
		
		# append the extra fittest individuals into the species
		for ind in bestInSpecies:
			pop.append(ind)
		
		# apply weight mutations
		print("*performing weight mutation")
		for ind in pop:
			if(ind.species == sys.maxsize and r.random() <= weightMutpb):
				toolbox.weightMutate(ind)
				# must invalidate individuals fitness if mutation applied
				del ind.fit_obj.values
		
		# apply node mutations
		print("*performing node mutation")
		for ind in pop:
			if(ind.species == sys.maxsize and r.random() <= nodeMutpb):
				print("Node mutation happening!")
				toolbox.nodeMutate(ind, gb)
				del ind.fit_obj.values

		# apply connection mutations
		print("*performing connection mutation")
		for ind in pop:
			if(ind.species == sys.maxsize and r.random() <= conMutpb):
				toolbox.connectionMutate(ind, gb)
				del ind.fit_obj.values

		# apply crossover
		print("*performing crossover")
		for child1, child2 in zip(pop[::2], pop[1::2]):
			if(child1.species == sys.maxsize and child2.species == sys.maxsize and r.random() <= cxPb):
				toolbox.mate(child1, child2)
				del child1.fit_obj.values
				del child2.fit_obj.values
		print("length of population")
		print(len(pop))
		#input()
		# must clear the dictionary of innovation numbers for the coming generation
		# only check to see if same innovation occurs twice in a single generation
		gb.clearDict()

	# return the population after it has been evolved
	return pop



# runs the main evolutionary loop if this file is ran from terminal
if __name__ == '__main__':

	NGEN = 40
	WEIGHT_MUTPB = .2
	NODE_MUTPB = .005
	CON_MUTPB = .01
	CXPB = -1.0
	THRESHOLD = 3.0
	ALPHA = 1.0
	THETA1 = 1.0
	THETA2 = 1.0
	THETA3 = 0.4
	NUM_IN = 2
	NUM_OUT = 1
	# main parameters: nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, thresh, alpha, theta1, theta2, theta3, numIn, numOut
	# run main EA loop
	finalPop = main(NGEN, WEIGHT_MUTPB, NODE_MUTPB, CON_MUTPB, CXPB, THRESHOLD, ALPHA, THETA1, THETA2, THETA3, NUM_IN, NUM_OUT)
	inputs = [[0,0],[0,1],[1,0],[1,1]]
	for ind in finalPop:
		print("\n")
		for ins in inputs:
			print(ind.getOutput(ins)[0])
		print("\n")
		input()