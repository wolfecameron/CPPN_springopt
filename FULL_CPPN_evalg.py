import copy
import random
'''
File that implements helper methods for the CPPN evolutionary algorithm
File contains a main variation algorithm, mutation algorithm, 
and a selection algorithm for populations of Genotypes
'''


'''
method to perform binary selection on a list of genotypes
chooses two random individuals at a time and selects one 
to place into the new population
process continues until a new population of same length is created
@param population the population from which is being selected
@return new population after selection is performed
'''
def binarySelect(population):
	#stores all selected individuals from binary tournaments
	newPop = []
	# all individuals get a chance to compete twice
	pop1 = copy.deepcopy(population)
	pop2 = copy.deepcopy(population)
	random.shuffle(pop1)
	random.shuffle(pop2)
	#performs binary selection on first copy of population
	while(len(pop1) > 0):
		# pop two individuals but only put one into new population
		ind1 = pop1.pop()
		ind2 = pop1.pop()
		if(ind1.fitness < ind2.fitness):
			newPop.append(ind1)
		else:
			newPop.append(ind2)
	#performs binary selection on second copy of population
	while(len(pop2) > 0):
		ind1 = pop2.pop()
		ind2 = pop2.pop()
		if(ind1.fitness < ind2.fitness):
			newPop.append(ind1)
		else:
			newPop.append(ind2)

	return newPop

'''
method for applying mutation/crossover to a population
@param mutpb probability that an individual in a population is mutated
@param cxpb probability that an individual in a population is crossed over
@param innovationMap dictionary containing key-value of (inNode,outNode) -> innovation number
@return new
'''
def applyMutation(population, mutpb, innovationMap, globalInnovation):
	# new population is created as old pop is traversed and mutated
	newPop = []
	for orgInd in range(len(population)):
		if(r.random() <= mutpb):
			mutType = random.random()
			if(0<= mutType < .25):
				population[orgInd].weightMutate(mutpb)
			elif(.25 <= mutType < .5):
				population[orgInd].activationMutate()
			elif(.5 <= mutType < .75):
				newData = population[orgInd].connectionMutate(innovationMap,globalInnovation)
				innovationMap = newData[0]
				globalInnovation = newData[1]
			else:
				newData = population[orgInd].nodeMutate(innovationMap, globalInnovation)
				innovationMap = newData[0]
				globalInnovation = newData[1]
	return (population, innovationMap, globalInnovation)

'''
method for applying crossover to an entire population
@param population the population of genotypes that is being crossed over
@return new population after crossover
'''
def applyCrossover(population, cxpb):
	# build the new population to return as the old population is traversed
	newPop = []
	# individuals are crossed over with those next to them
	# shuffle population to create new possibilities for crossover
	random.shuffle(population)
	for orgInd in range(len(population)):
		doCx = r.random()
		if(doCX <= cxpb and orgInd < len(population) - 1):
			newInd = population[orgInd].crossover(population[orgInd + 1])
			newPop.append(newInd)
		else:
			newPop.append(population[orgInd])
	return newPop