'''
This file contains all code for implementing CPPN using DEAP
CPPN implementation is recreated using creator in DEAP library
implementation details are same as other full CPPN files
'''
from deap import base
from deap import tools
from deap import algorithms
from deap import creator
from FULL_CPPN_struct import Genotype
from FULL_CPPN_deaphelp import weightMutate, conMutate, nodeMutate, xover, xover_avg
from FULL_CPPN_innovation import GlobalInnovation
import numpy as np
from FULL_CPPN_evalg import getSharingMatrix, speciatePopulationFirstTime, speciatePopulationNotFirstTime
from FULL_CPPN_evalg import getFittestFromSpecies, getNicheCounts, binarySelect
from FULL_CPPN_vis import visConnections, visHiddenNodes, findNumGoodSolutions
from FULL_CPPN_evaluation import evaluate_classification, evaluate_pic
from FULL_CPPN_gendata import genGaussianData, genCircularData, genXORData
from FULL_CPPN_getpixels import getBinaryPixels, getNormalizedInputs, graphImage
import random as r
import sys


''' ----- REGISTER ALL FUNCTIONS AND CLASSES WITH DEAP ----- '''

# create class for maximizing fitness and creating individual
# must name fitness atribute fit_obj because fitness is a instance variable of Genotype class
creator.create("FitnessMax", base.Fitness, weights = (1.0,))
creator.create("Individual", Genotype, fit_obj = creator.FitnessMax) 

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
NUM_IN = 2
NUM_OUT = 1
toolbox.register("individual", creator.Individual, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
POP_SIZE = 150
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n = POP_SIZE)

# register all functions needed for evolution in the toolbox
TOURN_SIZE = 3
toolbox.register("evaluate", evaluate_pic)
toolbox.register("select", binarySelect)
toolbox.register("tournSelect", tools.selTournament, fit_attr = "fitness")
toolbox.register("mate", xover_avg)
toolbox.register("weightMutate", weightMutate)
toolbox.register("connectionMutate", conMutate)
toolbox.register("nodeMutate", nodeMutate)
toolbox.register("map", map)

# generate the classification data set that will be used for evolution
DATA_SIZE = 100
MAX_VALUE = 2
DATA_SET = genXORData(DATA_SIZE, MAX_VALUE)

# sets global parameters for 2D structure being created by CPPN, generates inputs
NUM_X = 50
NUM_Y = 50
NORM_IN = getNormalizedInputs(NUM_X, NUM_Y)
FILE_PATH = '/home/wolfecameron/Desktop/CPPN_to/Images/spring9.png'
PIXELS = getBinaryPixels(FILE_PATH, NUM_X, NUM_Y)



'''
the main function for the DEAP evolutionary algorithm
the main EA loop is contained inside of this function
NOTE: pop size is set where the population function is registered
'''
def main(nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, thresh, alpha, theta1, theta2, theta3, numIn, numOut):
	pop = toolbox.population()
	# use global innovation object to track the creation of new innovation numbers during evolution
	gb = GlobalInnovation(numIn, numOut)
	
	# the following variables are used to track the improvement of species over generations
	# if a species' fitness becomes stagnant - it is penalized
	MIN_NUM_STAGNANT_GENERATIONS = 35
	STAGNATION_THRESHOLD = 1.05
	LAST_FITNESS = []
	CURRENT_STAG_GENS = []

	# the following is used for modifying the speciation threshold
	GENERATION_TO_MODIFY_THRESH = 30 # this is the first generation that the threshold can begin being adjusted
	DESIRED_NUM_SPECIES = 5
	THRESH_MOD = .1
	LAST_NUM_SPECIES = -1


	for g in range(NGEN):
		print("RUNNING GENERATION " + str(g))

		# use the following conditional to visualize certain properties of population near end of evolution
		if(g == NGEN - 1):
			visConnections(pop)
			visHiddenNodes(pop)

		# create a 2D array representing species from the population
		if(g == 0):
			species = speciatePopulationFirstTime(pop, thresh, theta1, theta2, theta3)
		else:
			species = speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3)

		# determine if speciation threshold needs to be modified and apply modification
		if(g >= GENERATION_TO_MODIFY_THRESH):
			numSpecies = len(species)
			# increase threshold if there are too many species and the number is still increasing
			if(numSpecies > DESIRED_NUM_SPECIES):
				if(LAST_NUM_SPECIES == -1 or numSpecies > LAST_NUM_SPECIES):
					thresh += THRESH_MOD
			# decrease theshold if there are too many species and the number of species is not increasing
			elif(numSpecies < DESIRED_NUM_SPECIES):
				if(LAST_NUM_SPECIES == -1 or numSpecies <= LAST_NUM_SPECIES):
					thresh -= THRESH_MOD


		# find all fitness values for individuals in population, update fitness tracking for species
		for specInd in range(len(species)):
			avgSpecFit = 0.0
			for ind in species[specInd]:
				# actual fitness value must be divided by the number of individuals in a given species
				# this keeps any given species from taking over a population - speciation fosters diversity
				fit = toolbox.evaluate(ind, PIXELS, NORM_IN, len(species[specInd]))
				avgSpecFit += fit[0]
				ind.fit_obj.values = fit
				ind.fitness = fit[0]
			# must find average fitness of species to compare against previous generation and see if species is stagnant
			avgSpecFit /= len(species[specInd])
			
			# check if fitness is stagnant for current generations and update stagnant counter appropriately
			if(specInd < len(LAST_FITNESS)):
				if(avgSpecFit/LAST_FITNESS[specInd] <= STAGNATION_THRESHOLD):
					CURRENT_STAG_GENS[specInd] = CURRENT_STAG_GENS[specInd] + 1
				else:
					# reset stagnation counter is a species improves enough to be above the threshold
					CURRENT_STAG_GENS[specInd] = 0
			
			# if this is the first generation for a species, append values for it into both stagnation-tracking lists
			else:
				LAST_FITNESS.append(avgSpecFit)
				CURRENT_STAG_GENS.append(0)

		# traverse the list of stagnance counters to see if any species need to be penalized for being stagnant
		index = 0
		for spec in CURRENT_STAG_GENS:
			# if stagnant generations too high, penalize the species
			if(spec >= MIN_NUM_STAGNANT_GENERATIONS):
				# penalizing stagnant species
				for org in species[index]:
					# penalization increases as the number of stagnant generations increases
					org.fitness /= (float(2*spec)/MIN_NUM_STAGNANT_GENERATIONS)
					org.fit_obj.values = (org.fitness,)	
			index += 1

		tournamentSelectSpecies = []

		# speciate the population after finding corresponding fitnesses
		print("Num Species: " + str(len(species)))
		# go through each species and select the best individuals from each species
		for specInd in range(len(species)):
			# set all species back to 0 first:
			for org in species[specInd]:
				org.species = sys.maxsize
			bestInd = toolbox.tournSelect(species[specInd], tournsize = 2, k = 1)[0]
			bestInd = bestInd.getCopy()
			tournamentSelectSpecies.append(bestInd)
		
		# fittest from species function selects all species representatives
		# and sets the species variable for the rest of the population to sys.maxsize
		fitTup = getFittestFromSpecies(species)
		bestInSpecies = fitTup[0]
		pop = fitTup[1]

		for org in tournamentSelectSpecies:
			bestInSpecies.append(org)	



		# select from rest of population to form the full sized population
		pop = toolbox.select(pop, bestInSpecies)
		
		# append the extra fittest individuals into the species
		#for ind in bestInSpecies:
		#	pop.append(ind)

		# only apply mutation if there will be another iteration of selection following this
		if(g < NGEN - 1):
			# apply weight mutations
			for ind in pop:
				if(ind.species == sys.maxsize and r.random() <= weightMutpb):
					toolbox.weightMutate(ind)
					# must invalidate individuals fitness if mutation applied
					del ind.fit_obj.values
			
			# apply node mutations
			for ind in pop:
				if(ind.species == sys.maxsize and r.random() <= nodeMutpb):
					toolbox.nodeMutate(ind, gb)
					del ind.fit_obj.values

			# apply connection mutations
			for ind in pop:
				if(ind.species == sys.maxsize and r.random() <= conMutpb):
					toolbox.connectionMutate(ind, gb)
					del ind.fit_obj.values
			
			# apply crossover
			# go through population looking at every pair of individuals next to each other 
			for child1Ind, child2Ind in zip(range(0,len(pop),2), range(1,len(pop),2)):
				interspecies_probability = .001 # probability individuals crossed over if not in same species
				child1 = pop[child1Ind]
				child2 = pop[child2Ind]
				dist = child1.getDistance(child2, theta1, theta2, theta3)

				# crossover happens with different probability depending if individuals in question are in same species
				if(child1.species == sys.maxsize and child2.species == sys.maxsize and dist < thresh and r.random() <= cxPb):
					# cross individuals over and put them into the population
					xTup = toolbox.mate(child1, child2)
					pop[child1Ind] = xTup[0]
					pop[child2Ind] = xTup[1]
					del pop[child1Ind].fit_obj.values
					del pop[child2Ind].fit_obj.values
				elif(child1.species == sys.maxsize and child2.species == sys.maxsize and r.random() <= interspecies_probability):
					xTup = toolbox.mate(child1, child2)
					pop[child1Ind] = xTup[0]
					pop[child2Ind] = xTup[1]
					del pop[child1Ind].fit_obj.values
					del pop[child2Ind].fit_obj.values
			

		# must clear the dictionary of innovation numbers for the coming generation
		# only check to see if same innovation occurs twice in a single generation
		gb.clearDict()

	# return the population after it has been evolved
	return pop



# runs the main evolutionary loop if this file is ran from terminal
if __name__ == '__main__':

	NGEN = 1000
	WEIGHT_MUTPB = .35
	NODE_MUTPB = .05
	CON_MUTPB = .1
	CXPB = .15
	THRESHOLD = 3.0
	ALPHA = 1.0
	THETA1 = 1.0
	THETA2 = 1.0
	THETA3 = 0.4
	NUM_IN = 2
	NUM_OUT = 1
	# main parameters: nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, thresh, alpha, theta1, theta2, theta3, numIn, numOut
	# run main EA loop
	finalPop = main(NGEN, WEIGHT_MUTPB, NODE_MUTPB, CON_MUTPB, CXPB, THRESHOLD, ALPHA, THETA1, THETA2, THETA3, NUM_IN, NUM_OUT)
	# averageSuccessful = 0.0
	# generate the classification data set that will be used for evolution
	DATA_SIZE = 100
	MAX_VALUE = 2
	n = 0
	for org in finalPop:
		outputs = []
		# get all outputs for every pixel in space of picture and put all into a numpy array
		for ins in NORM_IN:
			outputs.append(org.getOutput([ins[0], ins[1]])[0])
		outputs_np = np.array(outputs, copy = True)
		graphImage(outputs_np, NUM_X, NUM_Y)
		input("SHOWING INDIVIDUAL #" + str(n))
		n += 1


