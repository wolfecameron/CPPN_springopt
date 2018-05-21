'''
This file contains all helper functions for the evolutionary algorithm
created using DEAP in the _deapea py file. 

These functions are used to register mutations functions within the 
DEAP framework
'''
from FULL_CPPN_struct import Genotype
import sys

'''
function for applying weight mutation to an individual
registered as the mutation function in the DEAP toolbox
@param individual the organism that is being mutated
@param mutpb the probability of a mutation occurring
'''
def weightMutate(individual):
	# only mutate if the individual is not a species representative
	if(individual.species == sys.maxsize):
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
	# only mutate if not a representative for the species
	if(individual.species == sys.maxsize):
		# update innovation tracking variables each time connection added
		innovResult = globalInnovation.getNextInnov()
		innovResult = individual.connectionMutate(innovResult)
		globalInnovation.current = innovResult

	return  individual,


'''
method for applying node mutation to an individual
@param individual organism that is currently being mutated
@param nodePb probability that each individual will be node mutated
@param globalInnovation object used to track innovation numbers in a population
@return updated value of innovationMap and innovation number
'''
def nodeMutate(individual, globalInnovation):
	# only apply mutation if not a representative for a species
	if(individual.species == sys.maxsize):
		# update innovation tracking variables when node is added, this allows you 
		# to prevent the same mutation having different innov nums in same generation
		innovTup = individual.nodeMutate(globalInnovation.innovDict, globalInnovation.getNextInnov())
		# update tracking variables in the global innovation object
		globalInnovation.innovDict = innovTup[0]
		globalInnovation.current = innovTup[1]
	
	return individual,


'''
method for applying crossover to two individuals
@param population the population of genotypes that is being crossed over
@return new population after crossover
'''
def xover(individual1, individual2):
	# cross individuals over and return new one as long as neither are representatives
	# of a species
	if(individual1.species == sys.maxsize and individual2.species == sys.maxsize):
		(newInd1, newInd2) = individual1.crossoverReturnBoth(individual2)

	return (newInd1, newInd2)



