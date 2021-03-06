'''
This file contains all code for implementing CPPN using DEAP
It is very similar to the deapea file but this file implements
CPPN using the d parameter, which passes more information about the
picture being fitted to the CPPN
'''

import sys
import os

from deap import base, tools, algorithms, creator
import argparse
import numpy as np
import pickle
from scoop import futures

from FULL_CPPN_struct import Genotype
from FULL_CPPN_deaphelp import weightMutate, conMutate, nodeMutate, xover, xover_avg, actMutate, save_population
from FULL_CPPN_deaphelp import examine_population_dmat, get_file_name
from FULL_CPPN_innovation import GlobalInnovation
from FULL_CPPN_evalg import getSharingMatrix, speciatePopulationFirstTime, speciatePopulationNotFirstTime
from FULL_CPPN_evalg import getFittestFromSpecies, getNicheCounts, binarySelect
#from FULL_CPPN_vis import visConnections, visHiddenNodes, findNumGoodSolutions
from FULL_CPPN_evaluation import evaluate_classification, evaluate_pic, evaluate_pic_scoop, assign_fit_scoop
from FULL_CPPN_evaluation import evaluate_pic_dparam
#from FULL_CPPN_gendata import genGaussianData, genCircularData, genXORData
from FULL_CPPN_getpixels import getBinaryPixels, getNormalizedInputs, get_d_mat#, graphImage

# set up arguments to be parsed from the terminal
parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, 
	help="filepath to image that is being tested.")
parser.add_argument("seed", type=int, 
	help="Seed number for the current experiment.")
'''
parser.add_argument("weight", type=int, 
	help="Weight Mutation probability.")
parser.add_argument("node", type=int, 
	help="Node Mutation Probability.")
parser.add_argument("con", type=int, 
	help="Connection Mutation Probability.")
parser.add_argument("act", type=int, 
	help="Activation Mutation Probability.")
parser.add_argument("cross", type=int, 
	help="Crossover probability.")
'''
args = parser.parse_args()


# set numpy seed number for all random numbers
SEED = args.seed
np.random.seed(SEED)

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

# the following is the minimum proportion of material a solution must use 
# to not be penalized
MATERIAL_PENALIZATION_THRESHOLD = .1
MATERIAL_UNPRESENT_PENALIZATION = 2

# this value is what the d parameter weight should be initialized as
D_PARAM_WEIGHT = 1.16

# sets global parameters for 2D structure being created by CPPN, generates inputs
NORM_IN_FILE = open("norm_in.txt", "wb")
NUM_X = 75
NUM_Y = 75
NORM_IN = getNormalizedInputs(NUM_X, NUM_Y)
pickle.dump(NORM_IN, NORM_IN_FILE)


# must get filename from parser to complete file path
FILE_PATH = './fitting_images/' + args.path
PIXELS = getBinaryPixels(FILE_PATH, NUM_X, NUM_Y)


# generate the d parameter matrix and serialize it 
print("Generating distances matrix . . .")
D_MAT_FILE = open("d_mat.txt", "wb")
d_mat = get_d_mat(PIXELS, NUM_X, NUM_Y)
pickle.dump(d_mat, D_MAT_FILE)
print("Finished distances matrix . . . ")



''' ----- REGISTER ALL FUNCTIONS AND CLASSES WITH DEAP ----- '''

# create class for maximizing fitness and creating individual
# must name fitness atribute fit_obj because fitness is a instance variable of Genotype class
creator.create("FitnessMax", base.Fitness, weights = (1.0,))
creator.create("Individual", Genotype, fit_obj = creator.FitnessMax) 

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
NUM_IN = 3
NUM_OUT = 1
toolbox.register("individual", creator.Individual, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
POP_SIZE = 100
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n = POP_SIZE)

# register all functions needed for evolution in the toolbox
TOURN_SIZE = 3
toolbox.register("evaluate", evaluate_pic_dparam)
toolbox.register("assign_fit", assign_fit_scoop)
toolbox.register("select", binarySelect)
toolbox.register("tournSelect", tools.selTournament, fit_attr = "fitness")
toolbox.register("mate", xover_avg)
toolbox.register("weightMutate", weightMutate)
toolbox.register("connectionMutate", conMutate)
toolbox.register("nodeMutate", nodeMutate)
toolbox.register("activationMutate", actMutate)
toolbox.register("map", futures.map)


'''
the main function for the DEAP evolutionary algorithm
the main EA loop is contained inside of this function
NOTE: pop size is set where the population function is registered
'''
def main(nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, actMutpb, thresh, alpha, theta1, theta2, theta3, numIn, numOut):
	pop = toolbox.population()

	# change the weights for all individuals to intially find the perfect shape
	for ind in pop:
		ind.connections[0].setWeight(0)
		ind.connections[1].setWeight(0)
		ind.connections[2].setWeight(D_PARAM_WEIGHT)
		ind.connections[3].setWeight(0)

	# use global innovation object to track the creation of new innovation numbers during evolution
	gb = GlobalInnovation(numIn, numOut)


	# used to check whether a species fitness becomes stagnant
	LAST_FITNESS = []	
	CURRENT_STAG_GENS = []

	for g in range(NGEN):
		print("RUNNING GENERATION " + str(g))

		# use the following conditional to visualize certain properties of population near end of evolution
		#if(g == NGEN - 1):
		#	visConnections(pop)
		#	visHiddenNodes(pop)

		# create a 2D array representing species from the population
		if(g == 0):
			species = speciatePopulationFirstTime(pop, thresh, theta1, theta2, theta3)
		else:
			species = speciatePopulationNotFirstTime(pop, thresh, theta1, theta2, theta3)

		# determine if speciation threshold needs to be modified and apply modification
		# decrease threshold slowly to increase species, but increase quickly to keep to many
		# species from forming - thus the terms being different sizes
		if(g >= GENERATION_TO_MODIFY_THRESH):
			numSpecies = len(species)
			# increase threshold if there are too many species and the number is still increasing
			if(numSpecies > DESIRED_NUM_SPECIES):
				if(LAST_NUM_SPECIES == -1 or numSpecies > LAST_NUM_SPECIES):
					thresh += THRESH_MOD*2.0
			# decrease theshold if there are too many species and the number of species is not increasing
			elif(numSpecies < DESIRED_NUM_SPECIES):
				if(LAST_NUM_SPECIES == -1 or numSpecies <= LAST_NUM_SPECIES):
					thresh -= (THRESH_MOD/2.0)


		# find all fitness values for individuals in population, update fitness tracking for species
		for specInd in range(len(species)):
			avgSpecFit = 0.0
			# only the output pixels are mapped back, all evaluation must be done below
			outputs = toolbox.map(toolbox.evaluate, species[specInd])
			output_tups = []
			for o in outputs:
				output_tups.append((o[0], PIXELS, len(species[specInd]), 
						MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION))

			# map all outputs to the genotypes with their actual fitness assigned
			fitnesses = toolbox.map(toolbox.assign_fit, output_tups)		
			org_ind = 0
			for f in fitnesses:
				gen = species[specInd][org_ind]
				avgSpecFit += f[0]
				gen.fit_obj.values = f
				gen.fitness = f[0]
				org_ind += 1

			# must find average fitness of species to compare against previous generation and see if species is stagnant
			avgSpecFit /= len(species[specInd])
			
			'''
			org_ind = 0
			for out in outputs:
				gen = species[specInd][org_ind]
				out = out[0] # original list is inside of a tuple with the genotype
				proportion_mat_used = float(np.sum(out))/len(PIXELS)
				penalization = 1.0
				if(proportion_mat_used <= MATERIAL_PENALIZATION_THRESHOLD):
					penalization = 2.0 * (MATERIAL_PENALIZATION_THRESHOLD / (proportion_mat_used + .001))
				# find difference between the two pixel arrays
				ones_arr = np.ones((1, len(PIXELS)))
				diff = np.subtract(PIXELS, out)
				diff[diff>=.5] *= MATERIAL_UNPRESENT_PENALIZATION
				diff = np.fabs(diff)
				total_fit = (np.sum(np.subtract(ones_arr, diff)))/(len(species[specInd])*penalization)

				# actual fitness value must be divided by the number of individuals in a given species
				# this keeps any given species from taking over a population - speciation fosters diversity
				avgSpecFit += total_fit
				gen.fit_obj.values = (total_fit,)
				gen.fitness = total_fit
				spec_list.append(gen)
				org_ind += 1
			'''
			
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

		# only apply mutation if there will be another iteration of selection following this
		if(g < NGEN - 1):
			# apply weight mutations
			for ind in pop:
				if(ind.species == sys.maxsize and np.random.uniform() <= weightMutpb):
					toolbox.weightMutate(ind)
					# must invalidate individuals fitness if mutation applied
					del ind.fit_obj.values
			
			# apply node mutations
			for ind in pop:
				if(ind.species == sys.maxsize and np.random.uniform() <= nodeMutpb):
					toolbox.nodeMutate(ind, gb)
					del ind.fit_obj.values

			# apply connection mutations
			for ind in pop:
				if(ind.species == sys.maxsize and np.random.uniform() <= conMutpb):
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
				if(child1.species == sys.maxsize and child2.species == sys.maxsize and dist < thresh and np.random.uniform() <= cxPb):
					# cross individuals over and put them into the population
					xTup = toolbox.mate(child1, child2)
					pop[child1Ind] = xTup[0]
					pop[child2Ind] = xTup[1]
					del pop[child1Ind].fit_obj.values
					del pop[child2Ind].fit_obj.values
				elif(child1.species == sys.maxsize and child2.species == sys.maxsize and np.random.uniform() <= interspecies_probability):
					xTup = toolbox.mate(child1, child2)
					pop[child1Ind] = xTup[0]
					pop[child2Ind] = xTup[1]
					del pop[child1Ind].fit_obj.values
					del pop[child2Ind].fit_obj.values
			
			# apply activation mutation
			for ind in pop:
				if(ind.species == sys.maxsize and np.random.uniform() <= actMutpb):
					toolbox.activationMutate(ind)
					del ind.fit_obj.values

		# must clear the dictionary of innovation numbers for the coming generation
		# only check to see if same innovation occurs twice in a single generation
		gb.clearDict()

	# return the population after it has been evolved
	return pop



# runs the main evolutionary loop if this file is ran from terminal
if __name__ == '__main__':
	'''
	pop_tup = pickle.load(open('/home/wolfecameron/Desktop/CPPN_pop_result/CPPN_delete_con_test_7.txt', 'rb'))
	pop = pop_tup[0]
	for individual in pop:
		org = Genotype(2,1)
		org.connections = individual.connections
		org.nodes = individual.nodes
		org.gSize = individual.gSize
		output = []
		for ins in NORM_IN:
			output.append(org.getOutput(ins)[0])
		graphImage(np.array(output, copy=True), 50, 50, 200)
		org.graph_genotype()

	'''
	# the following are all parameter settings for main function
	NGEN = 800
	WEIGHT_MUTPB = .3#float(args.weight)/100.0 #.3 
	NODE_MUTPB = .03#float(args.node)/100.0 #.02
	CON_MUTPB = .25#float(args.con)/100.0 #.1
	CXPB = .1#float(args.cross)/100.0 #.1
	ACTPB = .05#float(args.act)/100.0 #.05
	THRESHOLD = 3.0
	ALPHA = 1.0
	THETA1 = 1.0
	THETA2 = 1.0
	THETA3 = 0.4
	NUM_IN = 2
	NUM_OUT = 1

	# main parameters: nGen, weightMutpb, nodeMutpb, conMutpb, cxPb, thresh, alpha, theta1, theta2, theta3, numIn, numOut
	# run main EA loop
	finalPop = main(NGEN, WEIGHT_MUTPB, NODE_MUTPB, CON_MUTPB, CXPB, ACTPB, THRESHOLD, ALPHA, THETA1, THETA2, THETA3, NUM_IN, NUM_OUT)
	#examine_population_dmat(finalPop, NUM_X, NUM_Y)

	file_name = get_file_name("/home/crwolfe/Documents/CPPN_test_env/CPPN_pop_result", "CPPN_dparam_test_")

	save_population(finalPop, SEED, file_name)
	

