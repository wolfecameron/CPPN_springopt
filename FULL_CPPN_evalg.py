import copy
import random as r
import sys
'''
File that implements helper methods for the CPPN evolutionary algorithm
File contains a main variation algorithm, mutation algorithm, 
and a selection algorithm for populations of Genotypes
'''

'''
method to perform tournament selection on a population
takes a tournament of individuals and puts the best one into the new population
@param population the population that is being selected out of
@param tournSize number of individuals in each tournament
@return new population of selected individuals
'''
def tournamentSelect(population, tournSize, partialPop):
	newPop = partialPop # best individuals of each species already in the population
	# select individuals for new population
	while(len(newPop) < len(population)):
		tournament = []
		# select k random individuals out of population
		for ind in range(tournSize):
			tournament.append(population[r.randint(0, len(population) - 1)])
		# put best of individuals into new population
		bestInd = None
		for ind in tournament:
			if(bestInd == None or ind.getFitness() < bestInd.getFitness()):
				bestInd = ind
		newPop.append(bestInd.getCopy())

	return newPop


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
		if(ind1.getFitness() < ind2.getFitness()):
			newPop.append(ind1.getCopy())
		else:
			newPop.append(ind2.getCopy())
	
	#performs binary selection on second copy of population
	while(len(partialPop) < len(population) and len(pop2) > 0):
		ind1 = pop2.pop()
		ind2 = pop2.pop()
		if(ind1.getFitness() < ind2.getFitness()):
			newPop.append(ind1.getCopy())
		else:
			newPop.append(ind2.getCopy())
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
@param population current pop that is being mutated
@param conPb probability a connection is going to be added to a certain individual
@param globalInnovation, next available innovation number to assign to a gene
@return updated version of globalInnovation number
'''
def applyConMutation(population, conPb, globalInnovation):
	for org in population:
		# go through each individual and decide if connection should be added
		if(r.random() <= conPb):
			# update innovation tracking variables each time connection added
			globalInnovation = org.connectionMutate(globalInnovation)
	return  globalInnovation

'''
method for applying node mutation to a population
@param nodePb probability that each individual in population will be node mutated
@param globalInnovation next available innovation number to assign to new genes
@return updated value of innovationMap and innovation number
'''
def applyNodeMutation(population, nodePb, globalInnovation):
	innovationMap = {}
	for org in population:
		# go through each individual and decide if node should be added
		if(r.random() <= nodePb):
			# update innovation tracking variables when node is added, this allows you 
			# to prevent the same mutation having different innov nums in same generation
			innovTup = org.nodeMutate(innovationMap, globalInnovation)
			innovationMap = innovTup[0]
			globalInnovation = innovTup[1]
	return globalInnovation


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
method for separating all members of a population into groups of species for the first time in evolution
@param pop population that is being separated into species
@param thresh maximum value of distance between to genomes to be in same species
@param theta1,2,3 weights used for calculating distance
@return 2D list containing all species
'''
def speciatePopulationFirstTime(pop, thresh, theta1, theta2, theta3):
	species = [[]]
	species[0].append(pop[0])
	species[0][0].species = 0
	for orgInd in range(1,len(pop)):
		currOrg = pop[orgInd]
		spInd = 0
		foundSpecies = False
		# find correct species for each individual and add it into the vector for that species
		while(spInd < len(species) and not foundSpecies):
			# get distance from original element in that species to decide if a member
			dist = currOrg.getAverageDistance(species[spInd],theta1,theta2,theta3)
			if(dist <= thresh):
				foundSpecies = True
			else:
				spInd += 1
		# either add to the species it was found to match or create new species
		if(foundSpecies):
			species[spInd].append(currOrg)
			currOrg.species = spInd
		else:
			species.append([currOrg])
			currOrg.species = len(species) - 1
	return species

'''
method for speciating population after it has already been speciated
@param pop population that is being separated into species
@param thresh maximum value of distance between two genomes to be in the same species
@param theta1,2,3 weights used for calculating distance
@return 2D list containing species
'''
def speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3):
	species = [[]]
	sortedPop = sorted(pop, key = lambda x: x.species)
	# for debugging purposes
	#for x in sortedPop:
	#	print(x.species)
	#input("check sorted")
	# store index and current species
	foundNotSpeciated = False
	popIndex = 1 # index in the sortedPop list
	currSpeciesInd = 0 # index of species that is currently being constructed 
	currSpecies = sortedPop[0].species # tracks number of species being currently constructed
	species[0].append(pop[0])

	# add all species that already have a species number
	while(not foundNotSpeciated and popIndex < len(sortedPop)):
		org = sortedPop[popIndex]
		if(org.species == sys.maxsize):
			foundNotSpeciated = True
		elif(org.species == currSpecies):
			species[currSpeciesInd].append(org)
			popIndex += 1
		else:
			currSpeciesInd += 1
			popIndex += 1
			currSpecies = org.species
			species.append([org])

	# add all species that need to be assigned a species
	for orgInd in range(popIndex, len(pop)):
		currOrg = sortedPop[orgInd]
		spInd = 0
		foundSpecies = False

		# loop through all species and find best one for current org
		while(spInd < len(species) and not foundSpecies):
			# get distance from original element in that species to decide if a member
			dist = currOrg.getAverageDistance(species[spInd], theta1, theta2, theta3)
			if(dist <= thresh):
				foundSpecies = True
			else:
				spInd += 1

		# decide where to add into species
		if(foundSpecies):
			# add org to species it was found to match and set its species number accordingly
			species[spInd].append(currOrg)
			currOrg.species = species[spInd][0].species
		else:
			# must create new species, make it's number one larger than current largest species num
			species.append([currOrg])
			currOrg.species = species[len(species) - 1][0].species + 1

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
		partialPop.append(fittest.getCopy())
	return partialPop

