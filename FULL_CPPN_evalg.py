import copy
import random as r
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
IMPLEMENT TOURNAMENT SELECTION AS WELL!
'''
def binarySelect(population, partialPop):
	#stores all selected individuals from binary tournaments
	newPop = partialPop # set equal to partial pop so best inds copied directly into new generation
	# all individuals get a chance to compete twice
	pop1 = copy.deepcopy(population)
	pop2 = copy.deepcopy(population)
	r.shuffle(pop1)
	r.shuffle(pop2)
	# ONLY CONTINUE ADDING ELEMENTS IF PARTIAL POP IS NOT OF SIZE EQUAL TO POPSIZE
	#performs binary selection on first copy of population
	while(len(partialPop) < len(population) and len(pop1) > 0):
		# pop two individuals but only put one into new population
		ind1 = pop1.pop()
		ind2 = pop1.pop()
		if(ind1.fitness < ind2.fitness):
			newPop.append(ind1)
		else:
			newPop.append(ind2)
	#performs binary selection on second copy of population
	while(len(partialPop) < len(population) and len(pop2) > 0):
		ind1 = pop2.pop()
		ind2 = pop2.pop()
		if(ind1.fitness < ind2.fitness):
			newPop.append(ind1)
		else:
			newPop.append(ind2)
	return newPop

'''
method for applying weight mutation to a population
@param mutpb probability that an individual in a population is mutated
@return (new population, new state of innovationMap, new global innovation number)
'''
def applyWeightMutation(population, mutpb):
	# mutate individuals weight iff random sample < mutpb
	for org in population:
		if(r.random() <= mutpb):
			org.weightMutate()

'''
method for applying connection mutation to a population
@param conPb probability a connection is going to be added to a certain individual
@param innovationMap, map of innovation numbers used to assign to new gene
@param globalInnovation, next available innovation number to assign to a gene
@return updated version of innovationMap and innovation number 
'''
def applyConMutation(population, conPb, innovationMap, globalInnovation):
	innovationMap_new = innovationMap
	globalInnovation_new = globalInnovation
	for org in population:
		# go through each individual and decide if connection should be added
		if(r.random() <= conPb):
			# update innovation tracking variables each time connection added
			conTup = org.connectionMutate(innovationMap_new, globalInnovation_new)
			innovationMap_new = conTup[0]
			globalInnovation_new = conTup[1]
	return (innovationMap_new, globalInnovation_new)

'''
method for applying node mutation to a population
@param nodePb probability that each individual in population will be node mutated
@innovationMap current list of genes and corresponding innovationNumbers
@param globalInnovation next available innovation number to assign to new genes
@return updated value of innovationMap and innovation number
'''
def applyNodeMutation(population, nodePb, innovationMap, globalInnovation):
	innovationMap_new = innovationMap
	globalInnovation_new = globalInnovation
	for org in population:
		# go through each individual and decide if node should be added
		if(r.random() <= nodePb):
			# update innovation tracking variables when node is added
			innovTup = org.nodeMutate(innovationMap_new, globalInnovation_new)
			innovationMap_new = innovTup[0]
			globalInnovation_new = innovTup[1]
	return (innovationMap_new, globalInnovation_new)


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
	r.shuffle(population)
	for orgInd in range(len(population)):
		doCx = r.random()
		if(doCx <= cxpb and orgInd < len(population) - 1):
			newInd = population[orgInd].crossover(population[orgInd + 1])
			newPop.append(newInd)
		else:
			newPop.append(population[orgInd])
	return newPop


'''
method for separating all members of a population into groups of species
@param pop population that is being separated into species
@param thresh maximum value of distance between to genomes to be in same species
@param theta1,2,3 weights used for calculating distance
@return 2D list containing all species
'''
def speciatePopulation(pop, thresh, theta1, theta2, theta3):
	species = [[]]
	species[0].append(pop[0])
	for orgInd in range(1,len(pop)):
		currOrg = pop[orgInd]
		spInd = 0
		foundSpecies = False
		# find correct species for each individual and add it into the vector for that species
		while(spInd < len(species) and not foundSpecies):
			# get distance from original element in that species to decide if a member
			dist = currOrg.getDistance(species[spInd][0],theta1,theta2,theta3)
			if(dist <= thresh):
				foundSpecies = True
			else:
				spInd += 1
		# either add to the species it was found to match or create new species
		if(foundSpecies):
			species[spInd].append(currOrg)
		else:
			species.append([currOrg])
	return species

'''
finds the fittest organism in each species and automatically puts it into the next generation
@param species Genotypes separated into a 2D array to model a species
@return a partial new population only containing the best species individuals
'''
def getFittestFromSpecies(species):
	partialPop = []
	for spec in species:
		fittest = None
		# find the fittest Genotype in a species
		for org in spec:
			if(fittest == None or fittest.getFitness() > org.getFitness()):
				fittest = org
		# append the fittest element from each species directly into next population
		partialPop.append(fittest)
	return partialPop

