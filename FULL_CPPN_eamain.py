from FULL_CPPN_struct import Genotype
from FULL_CPPN_evalg import binarySelect, applyWeightMutation, applyConMutation, applyNodeMutation, applyCrossover, speciatePopulation, getFittestFromSpecies
import matplotlib.pyplot as plt
import numpy as np

'''
This file contains the main driver for the evolutionary algorithm of CPPN
it uses functions from FULL_CPPN_evalg.py to select and mutate the population
final individuals are returned after the evolutionary algorithm is completed
'''

# following lists used to track data as the main function runs
AVERAGE_FITNESSES = []

'''
main function that runs the evolutionary algorithm
@param numIn the number of inputs into the original genotype
@param numOut the number of outputs from the original genotype
@param numGen the number of generations the evolution is run
@param popSize the number of individuals in each population
@param cxpb the probability of crossover
@param mutpb the probability of mutation
@return the final population after EA is completed
'''
def main(numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb):
	# always maintain a global state of all existing connections innov nums
	globalInnovation = ((numIn + 1) * numOut) + 1
	pop = []
	for loop in range(popSize):
		pop.append(Genotype(numIn, numOut))
	# ***** MAIN EA LOOP *****
	for g in range(numGen):
		print("RUNNING GENERATION " + str(g))
		# evaluate function handles speciation of population
		THRESHOLD = 4.0
		THETA1 = 1.0
		THETA2 = 1.0
		THETA3 = 0.4
		species = evaluateFitness(pop, THRESHOLD, THETA1, THETA2, THETA3)
		#print(len(species))
		partialPop = getFittestFromSpecies(species)
		pop = binarySelect(pop, partialPop)
		# always apply mutation and crossover after selection
		applyWeightMutation(pop, weight_mutpb)
		globalInnovation = applyConMutation(pop, con_mutpb, globalInnovation)
		globalInnovation = applyNodeMutation(pop, node_mutpb, globalInnovation)
		pop = applyCrossover(pop, cxpb)
		#print(len(pop))
	# return the resultant population after evolution done
	return pop

'''
evaluation function for the given evolutionary algorithm
this is often altered to needed constraints of the problem
@param population the population for which the fitness of 
all individuals is being found
@return population after fitness of all individuals is found
'''
def evaluateFitness(population, threshold, theta1, theta2, theta3):
	inputs = [[1,1],[0,1],[1,0],[0,0]]
	expectedOutput_tmp = [0,1,1,0]
	expectedOutput = np.array(expectedOutput_tmp, copy = True)
	species = speciatePopulation(population, threshold, theta1, theta2, theta3)
	print(len(species))
	# go through every species and calculate fitness for all individuals in the species
	total_fitness = 0.0
	for spInd in range(len(species)):
		specSize = len(species[spInd])
		for orgInd in range(len(species[spInd])):
			currOrg = species[spInd][orgInd]
			actualOutput_tmp = []
			for i in range(4):
				actualOutput_tmp.append(currOrg.getOutput(inputs[i])[0])
			actualOutput = np.array(actualOutput_tmp, copy = True)
			# must multiply original fitness by size of species to make speciation work
			# one species should not be able to dominate the population
			totalDifference = 0.0
			for x in range(len(actualOutput_tmp)):
				totalDifference += (actualOutput_tmp[x] - expectedOutput_tmp[x])**2
			species[spInd][orgInd].setFitness(totalDifference*len(species[spInd])) 
			total_fitness += totalDifference
	# append average fitness into global list so that fitness can be tracked
	AVERAGE_FITNESSES.append(total_fitness/len(population))
	# parse population from species list and return, all individuals have fitness assigned
	return species


# main function for running EA
if __name__ == "__main__":
	 # order of parameters for main : (numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb)
	numIn = 2
	numOut = 1
	numGen = 100
	popSize = 150
	weight_mutpb = .8
	con_mutpb = .3
	node_mutpb = .15
	cxpb = .05
	finalPop = main(numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb)
	ind = finalPop[25]
	print(ind.getOutput([0,0])[0])
	print(ind.getOutput([0,1])[0])
	print(ind.getOutput([1,0])[0])
	print(ind.getOutput([1,1])[0])
	plt.plot(AVERAGE_FITNESSES)
	plt.title("XOR - CPPN")
	plt.ylabel("Average Fitness")
	plt.xlabel("Generation")
	plt.show()