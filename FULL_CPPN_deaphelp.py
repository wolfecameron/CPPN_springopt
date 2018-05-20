'''
This file contains all helper functions for the evolutionary algorithm
created using DEAP in the _deapea py file. 

These functions are used to register mutations functions within the 
DEAP framework
'''
from FULL_CPPN_struct import Genotype

'''
function for applying weight mutation to an individual
registered as the mutation function in the DEAP toolbox
@param individual the organism that is being mutated
@param mutpb the probability of a mutation occurring
'''
def weightMutate(individual, mutpb):
	# only mutate if the individual is not a species representative
	if(individual.species == sys.maxsize and r.random() <= mutpb):
			individual.weightMutate()
	# must return as tuple to be compatible with DEAP
	return (individual,)

'''
method for applying connection mutation to an individual
@param population current pop that is being mutated
@param conPb probability a connection is going to be added to a certain individual
@param globalInnovation, next available innovation number to assign to a gene
@return updated version of globalInnovation number
'''
def applyConMutation(individual, conPb, globalInnovation):
	# only mutate if not a representative for the species
	if(individual.species == sys.maxsize):
		# go through each individual and decide if connection should be added
		if(r.random() <= conPb):
			# update innovation tracking variables each time connection added
			innovResult = globalInnovation.getNextInnov()
			innovResult = individual.connectionMutate(innovResult)
			# update global innovation counter if a new innovation value is assigned to the connection
			if(innovResult != globalInnovation.current):
				globalInnovation.incrementInnov()

	
	return  individual



