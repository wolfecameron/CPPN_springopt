from FULL_CPPN_struct import Genotype
from FULL_CPPN_evalg import binarySelect, applyMutation, applyCrossover

'''
This file contains the main driver for the evolutionary algorithm of CPPN
it uses functions from FULL_CPPN_evalg.py to select and mutate the population
final individuals are returned after the evolutionary algorithm is completed
'''

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
def main(numIn, numOut, numGen, popSize, cxpb, mutpb):
	# always maintain a global state of all existing connections innov nums
	innovationMap = getOriginalInnovationMap(numIn,numOut)
	globalInnovation = (numIn*numOut) + 1
	pop = []
	for loop in range(popSize):
		pop.append(Genotype(numIn, numOut))
	# ***** MAIN EA LOOP *****
	for g in range(numGen):
		# evaluate function handles speciation of population
		pop = evaluateFitness(pop)
		pop = binarySelect(pop)
		# always apply mutation and crossover after selection
		popTup = applyMutation(pop)
		pop = popTup[0]
		innovationMap = popTup[1]
		globalInnovation = popTup[2]
		pop = applyCrossover(pop)
	# return the resultant population after evolution done
	return pop

'''
evaluation function for the given evolutionary algorithm
this is often altered to needed constraints of the problem
@param population the population for which the fitness of 
all individuals is being found
@return population after fitness of all individuals is found
'''
def evaluateFitness(population):
	inputs = [(1,1),(0,1),(1,0),(0,0)]
	expectedOutput_tmp = [0,1,1,0]
	expectedOutput = np.array(expectedOutput_tmp, copy = True)
	species = speciatePopulation(population)
	# go through every species and calculate fitness for all individuals in the species
	for spInd in range(len(species)):
		specSize = len(species[spInd])
		for orgInd in range(len(species[spInd])):
			currOrg = species[spInd][orgInd]
			actualOutput_tmp = []
			for i in range(4):
				actualOutput_tmp.append(currOrg.getOutput(inputs[i]))
			actualOutput = np.array(actualOutput_tmp, copy = True)
			# must multiply original fitness by size of species to make speciation work
			# one species should not be able to dominate the population
			currOrg.setFitness(np.sum(np.square(np.subtract(actualOutput,expectedOutput)))*specSize)
	# parse population from species list and return
	newPop = []
	for spec in species:
		for org in spec:
			newPop.append(org)
	return newPop


'''
function to create the original dictionary of innovation numbers
before EA is run
@param numIn number of inputs to each genotype
@param numOut number of outputs from each genotype
@return the original innovation map for evolution process
'''
def getOriginalInnovationMap(numIn,numOut):
	# first connections from input to output all have a unique innovation number
	innovationMap = {}
	counter = 0
	for inInd in range(numIn + 1):
		conTup = (inInd, numIn + 1)
		innovationMap[conTup] = counter
		counter += 1

