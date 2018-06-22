'''
This file contains all helper functions for the evolutionary algorithm
created using DEAP in the _deapea py file. 

These functions are used to register mutations functions within the 
DEAP framework
'''

import sys

import numpy as np

from FULL_CPPN_struct import Genotype

'''
function for applying weight mutation to an individual
registered as the mutation function in the DEAP toolbox
@param individual the organism that is being mutated
@param mutpb the probability of a mutation occurring
'''
def weightMutate(individual):
	individual.weightMutate()
	# must return as tuple to be compatible with DEAP
	return individual,

'''
method for applying connection mutation to an individual
@param population current pop that is being mutated
@param conPb probability a connection is going to be added to a certain individual
@param globalInnovation, next available innovation number to assign to a gene
@return updated version of globalInnovation number
'''
def conMutate(individual, globalInnovation):
	# update innovation tracking variables each time connection added
	innovResult = globalInnovation.getNextInnov()
	globalInnovation.current = individual.connectionMutate(innovResult)

	return  individual,

''' 
method for applying an activation mutation in an individual 
@param individual the individual that is being mutated
@return the individual in the form of a tuple
'''
def actMutate(individual):
	# just use mutation function built into the genotype class
	individual.activationMutate()

	return individual,


'''
method for applying node mutation to an individual
@param individual organism that is currently being mutated
@param nodePb probability that each individual will be node mutated
@param globalInnovation object used to track innovation numbers in a population
@return updated value of innovationMap and innovation number
'''
def nodeMutate(individual, globalInnovation):
	# update innovation tracking variables when node is added, this allows you 
	# to prevent the same mutation having different innov nums in same generation
	innovTup = individual.nodeMutate(globalInnovation.innovDict, globalInnovation.getNextInnov())
	# update tracking variables in the global innovation object
	globalInnovation.innovDict = innovTup[0]
	globalInnovation.current = innovTup[1]
	
	return individual,


'''
method for applying crossover to two individuals
@param individua1,2 the individuals that are being crossed over
@return child and parent ind resulting from the crossover
'''
def xover(individual1, individual2):
	# cross individuals over and return both new individuals
	(newInd1, newInd2) = individual1.crossoverReturnBoth(individual2)

	return (newInd1, newInd2)

'''
same as above exepct instead of using the regular crossover function 
the average crossover function is used
@param individual1,2 the individuals being crossed over
@return child and parent ind resulting from the crossover
'''
def xover_avg(individual1, individual2):
	# cross individuals over
	(newInd1, newInd2) = individual1.crossoverAvg(individual2)

	return (newInd1, newInd2)


'''
this method takes a partial population that was yielded by selecting 
from species and clones individuals to make the population have the 
correct number of individuals
@param partialPop the partial population that needs to be cloned to create a full population
@param popSize the desired size of the resulting population
@return population of indivdiuals with size == popSize
'''
def makeFullPop(partialPop, popSize):
	# start at a random location in the partial population and begin cloning individuals
	ogSize = len(partialPop)
	index = np.random.randint(0, len(partialPop) - 1)
	# continually add copies of individuals for the partial population
	# until partial population is of the correct size
	while(len(partialPop) < popSize):
		currentOrg = partialPop[index % ogSize].getCopy()
		currentOrg.species = sys.maxsize
		partialPop.append(currentOrg)
		index += 1

	return partialPop

'''
activates a CPPN over a range of values and appends all outputs
into an array which can then be used to create a heatmap of the CPPN
output, used to visualize results of data set problems for CPPN
@param org the CPPN that is being activated
@param maxValue the maximum value within the CPPNs range of activation
@param step the distance between successive activations of the CPPN
@return numpy array containing all outputs that is resized properly to be put into the heat map
'''
def getOutputsForHeatMap(org, maxValue, step):
	outputs = []
	# start activating at upper left corner of range
	# move down the column of pixels then move to the next row
	# until the bottom right corner is reached
	xVal = -maxValue
	while(xVal <= maxValue):
		yVal = maxValue
		while(yVal >= -maxValue):
			outputs.append(org.getOutput([xVal, yVal])[0])
			yVal -= step
		xVal += step

	# put values into a numpy array and reshape it based on maxValue and step before returning
	outputs_np = np.array(outputs, copy = True)
	outputs_np = np.reshape(outputs_np, (int(maxValue*2/step), int(maxValue*2/step)))
	return outputs_np






