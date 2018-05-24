'''
This file contains all helper functions for the evolutionary algorithm
created using DEAP in the _deapea py file. 

These functions are used to register mutations functions within the 
DEAP framework
'''
from FULL_CPPN_struct import Genotype
import sys
import random as r

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
@param population the population of genotypes that is being crossed over
@return new population after crossover
'''
def xover(individual1, individual2):
	# cross individuals over and return both new individuals
	(newInd1, newInd2) = individual1.crossoverReturnBoth(individual2)

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
	index = r.randint(0, len(partialPop) - 1)
	# continually add copies of individuals for the partial population
	# until partial population is of the correct size
	while(len(partialPop) < popSize):
		currentOrg = partialPop[index % ogSize].getCopy()
		currentOrg.species = sys.maxsize
		partialPop.append(currentOrg)
		index += 1

	return partialPop





