import copy
import random as r
import numpy as np
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
			if(bestInd == None or ind.getFitness() > bestInd.getFitness()):
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
		if(ind1.getFitness() > ind2.getFitness()):
			newPop.append(ind1.getCopy())
		else:
			newPop.append(ind2.getCopy())
	
	#performs binary selection on second copy of population
	while(len(partialPop) < len(population) and len(pop2) > 0):
		ind1 = pop2.pop()
		ind2 = pop2.pop()
		if(ind1.getFitness() > ind2.getFitness()):
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
		# only apply mutation if not a representative for the species
		if(org.species == sys.maxsize and r.random() <= mutpb):
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
		# only mutate if not a representative for the species
		if(org.species == sys.maxsize):
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
		# only apply mutation if not a representative for a species

		if(org.species == sys.maxsize):
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
	for orgInd in range(len(population) - 1):
		if(population[orgInd].species == sys.maxsize):
			if(r.random() <= cxpb):
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
			# get distance from representative element in that species - check if below threshold
			dist = currOrg.getDistance(species[spInd][0], theta1, theta2, theta3)
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
method for speciating population after it has already been speciated
@param pop population that is being separated into species
@param thresh maximum value of distance between two genomes to be in the same species
@param theta1,2,3 weights used for calculating distance
@return 2D list containing species
'''
def speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3):
	species = [[]]
	sortedPop = sorted(pop, key = lambda x: x.species)

	# store index and current species
	foundNotSpeciated = False
	species[0].append(pop[0])
	index = 1 # index in the sortedPop lists
	# add all species that already have a species number
	while(not foundNotSpeciated and index < len(sortedPop)):
		org = sortedPop[index]
		if(org.species == sys.maxsize):
			foundNotSpeciated = True
#		elif(org.species == currSpecies):
#			species[currSpeciesInd].append(org)
#			popIndex += 1
		else:
			index += 1
			species.append([org])

	# add all species that need to be assigned a species
	for orgInd in range(index, len(pop)):
		currOrg = sortedPop[orgInd]
		spInd = 0
		foundSpecies = False

		# loop through all species and find best one for current org
		while(spInd < len(species) and not foundSpecies):
			# get distance from representative element in that species to decide if a member
			dist = currOrg.getDistance(species[spInd][0], theta1, theta2, theta3)
			if(dist <= thresh):
				foundSpecies = True
			else:
				spInd += 1

		# decide where to add into species
		if(foundSpecies):
			# add org to species it was found to match and set its species number accordingly
			species[spInd].append(currOrg)
		else:
			# must create new species, make it's number one larger than current largest species num
			species.append([currOrg])
		currOrg.species = spInd
	#print(len(species))
	return species


'''
finds the fittest organism in each species and automatically puts it into the next generation
@param species Genotypes separated into a 2D array to model a species
@return a partial new population only containing the best species individuals
'''
def getFittestFromSpecies(species):
	# store list of best individuals and the full population with species set to 0
	partialPop = []
	newPop = []
	for specInd in range(len(species)):
		fittest = None
		# find the fittest Genotype in a species
		for orgInd in range(len(species[specInd])):
			# get current organism and reset its species
			org = species[specInd][orgInd]
			org.species = sys.maxsize
			newPop.append(org)
			# update fittest individuals as you move through the species
			# only append to new pop if it's known that a given org is not the fittest
			if(fittest == None or fittest.getFitness() < org.getFitness()):
				fittest = org

		# append the fittest element from each species directly into next population
		# assign correct species number - all others reset to default values to be reassigned
		fittest = fittest.getCopy()
		fittest.species = specInd
		partialPop.append(fittest)

	return (partialPop, newPop)

'''
evaluation function for the given evolutionary algorithm
this is often altered to needed constraints of the problem
@param population the population for which the fitness of 
all individuals is being found
@return population after fitness of all individuals is found
return has average fitness at the second index of the returned tuple
'''
def evaluateFitness(population, threshold, theta1, theta2, theta3, g):
	inputs = [[1,1],[0,1],[1,0],[0,0]]
	expectedOutput_tmp = [0,1,1,0]
	expectedOutput = np.array(expectedOutput_tmp, copy = True)
	if(g == 0):
		species = speciatePopulationFirstTime(population, threshold, theta1, theta2, theta3)
	else:
		species = speciatePopulationNotFirstTime(population, threshold, theta1, theta2, theta3)
	#print(len(species))
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
				totalDifference += (1-(actualOutput_tmp[x] - expectedOutput_tmp[x])**2)
			species[spInd][orgInd].setFitness(totalDifference) 
			total_fitness += totalDifference

	# parse population from species list and return, all individuals have fitness assigned
	return (species, totalFitness/len(population))

'''
evaluation function for the given evolutionary algorithm
this is often altered to needed constraints of the problem
@param population the population for which the fitness of 
all individuals is being found
@return population after fitness of all individuals is found
return has average fitness at the second index of the returned tuple
'''
def evaluateFitness_fitsharing(population, threshold, theta1, theta2, theta3, g):
	inputs = [[1,1],[0,1],[1,0],[0,0]]
	expectedOutput_tmp = [0.0,1.0,1.0,0.0]
	expectedOutput = np.array(expectedOutput_tmp, copy = True)
	if(g == 0):
		species = speciatePopulationFirstTime(population, threshold, theta1, theta2, theta3)
	else:
		species = speciatePopulationNotFirstTime(population, threshold, theta1, theta2, theta3)
	#print(len(species))
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
				# subtract difference squared from one so that fitness can be maximized
				totalDifference += (1 - (actualOutput_tmp[x] - expectedOutput_tmp[x])**2)
			species[spInd][orgInd].setFitness(totalDifference/len(species[spInd])) 
			total_fitness += totalDifference/len(species[spInd])
	
	# return with all fitnesses assigned
	return (species, total_fitness/len(population))


'''
another fitness evaluation function using niche count to calculate fitness
@params same as other fitness evaluations
@return population and average fitness in a tuple
'''
def evaluateFitness_nichecount(population, threshold, theta1, theta2, theta3, g):
	# alpha is a parameter for tuning fitness sharing function
	ALPHA = 1 
	inputs = [[1,1],[0,1],[1,0],[0,0]]
	expectedOutput_tmp = [0.0,1.0,1.0,0.0]
	expectedOutput = np.array(expectedOutput_tmp, copy = True)
	sharingMatrix = getSharingMatrix(population, threshold, ALPHA, theta1, theta2, theta3)
	# go through every species and calculate fitness for all individuals in the species
	total_fitness = 0.0
	# create species matrix for selection purposes, put best of each species automatically forward
	if(g == 0):
		species = speciatePopulationFirstTime(population, threshold, theta1, theta2, theta3)
	else:
		species = speciatePopulationNotFirstTime(population, threshold, theta1, theta2, theta3)
	# row variable used to track row position in the sharing matrix
	row = 0
	for spInd in range(len(species)):
		currSpecies = species[spInd]
		for orgInd in range(len(currSpecies)):
			currOrg = species[spInd][orgInd]
			actualOutput_tmp = []
			for i in range(4):
				actualOutput_tmp.append(currOrg.getOutput(inputs[i])[0])
			actualOutput = np.array(actualOutput_tmp, copy = True)
			# must multiply original fitness by size of species to make speciation work
			# one species should not be able to dominate the population
			totalDifference = 0.0
			# nicheCount can be found by summing the row in sharing matrix corresponding to a given organism
			nicheCount = np.sum(sharingMatrix[row])
			for x in range(len(actualOutput_tmp)):
				# subtract difference squared from one so that fitness can be maximized
				totalDifference += (1 - (actualOutput_tmp[x] - expectedOutput_tmp[x])**2)
			totalDifference = totalDifference**2
			species[spInd][orgInd].setFitness(totalDifference/nicheCount) 
			total_fitness = totalDifference/nicheCount
			row += 1
	# return with all fitnesses assigned
	return (species, total_fitness/len(population))


'''
method for generating a map that stores sharing function between all 
individuals of a population, later used for explicit fitness sharing
@param population the pop for which sharing matrix is being generated
@param threshold maximum distance between networks to be same species
@param alpha parameter for fitness sharing function - generally set to 1 or 2
@param theta1-3 parameters for calculating distance between genomes
@return matrix containing all sharing information between species
'''
def getSharingMatrix(population, threshold, alpha, theta1, theta2, theta3):
	# stores all sharing info
	result = np.ones((len(population), len(population)))
	for ind1 in range(len(population)):
		for ind2 in range(len(population)):
			# order does not matter, matrix is symmetric
			# all diagonal entries should be 1, hence > and not >=
			if(ind2 > ind1):
				org1 = population[ind1]
				org2 = population[ind2]
				distance = org1.getDistance(org2, theta1, theta2, theta3)
				result[ind1][ind2] = calculateSharingFunction(distance, threshold, alpha)
				result[ind2][ind1] = result[ind1][ind2]
	# return matrix containing all fitness sharing values
	return result

'''
method for creating a list of niche counts from a sharingMatrix
@param sharingMatrix the sharing matrix for which the niche counts are being found
@return a list containing all niche counts for organisms
'''
def getNicheCounts(sharingMatrix):
	result = []
	row = 0
	# go through each row in the sharing matrix and find its sum
	while(row < sharingMatrix.shape[0]):
		result.append(np.sum(sharingMatrix[row]))
		row += 1

	return result


'''
helper function for sharing matrix
takes hamming distance of two genomes and converts it
into the output of the sharing function
@param distance hamming distance between genomes
@param threshold speciation threshold
@param alpha fitness sharing parameter - usually 1 or 2
@return sharing function value for given distance and threshold
'''
def calculateSharingFunction(distance, threshold, alpha):
	if(distance <= threshold):
		return 1 - (distance/threshold)**alpha
	else:
		return 0

	

