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
	for g in range(numGen):
		# evaluate function handles speciation of population
		evaluateFitness(pop)
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

