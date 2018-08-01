"""This file contains the evolutionary algorithm using deap that
is implemented for novelty search using the CPPN
"""

import sys
import os
import copy

from deap import base, tools, algorithms, creator
import argparse
import numpy as np
import pickle
from scoop import futures

from FULL_CPPN_struct import Genotype
from FULL_CPPN_deaphelp import weightMutate, conMutate, nodeMutate, xover, xover_avg, actMutate, save_population
from FULL_CPPN_deaphelp import examine_population_dmat, get_file_name, get_pareto_front
from FULL_CPPN_innovation import GlobalInnovation
from FULL_CPPN_evalg import getSharingMatrix, speciatePopulationFirstTime, speciatePopulationNotFirstTime
from FULL_CPPN_evalg import getFittestFromSpecies, getNicheCounts, binarySelect
from FULL_CPPN_vis import visConnections, visHiddenNodes, findNumGoodSolutions, plot_pareto_front, get_n_colors
from FULL_CPPN_evaluation import evaluate_novelty, evaluate_pic_scoop
from FULL_CPPN_evaluation import evaluate_pic_dparam, evaluate_nov_pic
#from FULL_CPPN_gendata import genGaussianData, genCircularData, genXORData
from FULL_CPPN_getpixels import getBinaryPixels, getNormalizedInputs, get_d_mat, graphImage

# set up arguments to be parsed from the terminal
parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, 
	help="filepath to image that is being tested.")
parser.add_argument("seed", type=int, 
	help="Seed number for the current experiment.")
parser.add_argument("ngen", type=int,
	help="Number of generations to run the evolution.")

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
MATERIAL_PENALIZATION_THRESHOLD = .2
MATERIAL_UNPRESENT_PENALIZATION = 2


# sets global parameters for 2D structure being created by CPPN, generates inputs
NORM_IN_FILE = open("norm_in.txt", "wb")
NUM_X = 75
NUM_Y = 75
NORM_IN = getNormalizedInputs(NUM_X, NUM_Y)
pickle.dump(NORM_IN, NORM_IN_FILE)


# must get filename from parser to complete file path
FILE_PATH = './fitting_images/' + args.path
PIXELS = getBinaryPixels(FILE_PATH, NUM_X, NUM_Y)


# determines when to save the current population
NGEN_TO_SAVE = args.ngen - 1 # save every n generations

NOV_ARCHIVE = []
K_VAL = 5
ARCHIVE_PROB = 0.0

''' ----- REGISTER ALL FUNCTIONS AND CLASSES WITH DEAP ----- '''

# create class for maximizing fitness and creating individual
# must name fitness atribute fit_obj because fitness is a instance variable of Genotype class
creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
creator.create("Individual", Genotype, fitness=creator.FitnessMulti) 

# initialize the toolbox
toolbox = base.Toolbox()

# register function to create individual in the toolbox
NUM_IN = 2
NUM_OUT = 1
toolbox.register("individual", creator.Individual, NUM_IN, NUM_OUT)

# register function to create population in the toolbox
POP_SIZE = 50
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n = POP_SIZE)

# register all functions needed for evolution in the toolbox
TOURN_SIZE = 2
toolbox.register("evaluate", evaluate_pic_scoop)
toolbox.register("assign_fit", evaluate_nov_pic)
toolbox.register("select", tools.selNSGA2)
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
	
	# instantiate the population
	pop = toolbox.population()
	
	# use to track effectiveness of mutations
	dom_good = 0
	dom_bad = 0
	non_dom = 0
	
	
	# assign fitness to the initial population
	outputs = list(toolbox.map(toolbox.evaluate, pop))

	# create full matrices of archived and current vectors
	full_pop_vecs = np.vstack(outputs)
	# only create the archive vectors if there are individuals in the archive
	if(len(NOV_ARCHIVE) > 0):
		# must grab the numpy arrays out of each tuple in novelty archive
		full_archive_vecs = np.vstack([x[1] for x in NOV_ARCHIVE])
	else:
		full_archive_vecs = np.array([[]])

	# create tuples that can be fed into the novelty fitness assignment function
	output_tups = [(gen, vec[0], PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
		full_pop_vecs, full_archive_vecs, K_VAL) for gen, vec in zip(pop, outputs)]

	# map all outputs to the genotypes with their actual fitness assigned
	fitnesses = list(toolbox.map(toolbox.assign_fit, output_tups))
	
	'''
	# find all output lists that should be added to the archive
	for index in range(len(fitnesses)):
		# randomly add individuals into the archive based on a probability
		if(np.random.uniform() <= ARCHIVE_PROB):
			NOV_ARCHIVE.append((pop[index], outputs[index]))
	'''

	org_ind = 0
	for f,o in zip(fitnesses, outputs):
		gen = pop[org_ind]
		gen.fitness.values = f
		org_ind += 1
	
	
	# use global innovation object to track the creation of new innovation numbers during evolution
	gb = GlobalInnovation(numIn, numOut)


	# run the evolution loop
	for g in range(NGEN):
		print("RUNNING GENERATION " + str(g))

		'''
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
		#for specInd in range(len(species)):
		#avgSpecFit = 0.0
		
		# only the output pixels are mapped back, all evaluation must be done below
		outputs = list(toolbox.map(toolbox.evaluate, pop))

		# create full matrices of archived and current vectors
		full_pop_vecs = np.vstack(outputs)
		# only create the archive vectors if there are individuals in the archive
		if(len(NOV_ARCHIVE) > 0):
			# must grab the numpy arrays out of each tuple in novelty archive
			full_archive_vecs = np.vstack([x[1] for x in NOV_ARCHIVE])
		else:
			full_archive_vecs = np.array([[]])

		# create tuples that can be fed into the novelty fitness assignment function
		output_tups = [(vec[0], PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
				 full_pop_vecs, full_archive_vecs, K_VAL) for vec in outputs]

		# map all outputs to the genotypes with their actual fitness assigned
		fitnesses = list(toolbox.map(toolbox.assign_fit, output_tups))
		
		# find all output lists that should be added to the archive
		for index in range(len(fitnesses)):
			# randomly add individuals into the archive based on a probability
			if(np.random.uniform() <= ARCHIVE_PROB):
				NOV_ARCHIVE.append((pop[index], outputs[index]))

		org_ind = 0
		for f,o in zip(fitnesses, outputs):
			#if(np.sum(o)/(NUM_X*NUM_Y) < MATERIAL_PENALIZATION_THRESHOLD or 
				#	np.sum(o)/(NUM_X*NUM_Y) > (1 - MATERIAL_PENALIZATION_THRESHOLD)):
				# penalize the solution for not having enough or too much material
				#f = (f[0]/2,)
			
			gen = pop[org_ind]
			gen.fit_obj.values = f
			gen.fitness = f
			org_ind += 1


		
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
		
		# go through each species and select the best individuals from each species
		for specInd in range(len(species)):
			# set all species back to 0 first:
			for org in species[specInd]:
				org.species = sys.maxsize
			bestInd = toolbox.tournSelect(species[specInd], tournsize = TOURN_SIZE, k = 1)[0]
			bestInd = bestInd.getCopy()
			tournamentSelectSpecies.append(bestInd)


		# fittest from species function selects all species representatives
		# and sets the species variable for the rest of the population to sys.maxsize
		fitTup = getFittestFromSpecies(species)
		bestInSpecies = fitTup[0]
		pop = fitTup[1]

		for org in tournamentSelectSpecies:
			bestInSpecies.append(org)	

		'''

		# only apply mutation if there will be another iteration of selection following this
		mutants = []
		
		for ind in pop:
			new_ind = copy.deepcopy(ind)
			# apply weight mutation
			if(np.random.uniform() <= weightMutpb):
				new_ind = toolbox.weightMutate(new_ind)[0]
				'''
				output = toolbox.evaluate(new_ind)
				output_tup = (new_ind, output, PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
					np.array([[]]), np.array([[]]), 1)
				fit = toolbox.assign_fit(output_tup)
				new_ind.fitness.values = fit
				if(new_ind.fitness.dominates(ind.fitness)):
					dom_good += 1
				elif(ind.fitness.dominates(new_ind.fitness)):
					dom_bad += 1
				else:
					non_dom += 1
				'''

			# apply node mutation
			if(np.random.uniform() <= nodeMutpb):
				new_ind = toolbox.nodeMutate(new_ind, gb)[0]

			# apply onnection mutation
			if(np.random.uniform() <= conMutpb):
				new_ind = toolbox.connectionMutate(new_ind, gb)[0]
	
			# apply activation mutation
			if(np.random.uniform() <= actMutpb):
				new_ind = toolbox.activationMutate(new_ind)[0]
				'''
				output = toolbox.evaluate(new_ind)
				output_tup = (new_ind, output, PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
					np.array([[]]), np.array([[]]), 1)
				fit = toolbox.assign_fit(output_tup)
				new_ind.fitness.values = fit
				if(new_ind.fitness.dominates(ind.fitness)):
					dom_good += 1
				elif(ind.fitness.dominates(new_ind.fitness)):
					dom_bad += 1
				else:
					non_dom += 1
				'''
			# append the newly mutated individuals to a separate list
			mutants.append(new_ind)
		
		
		# apply crossover
		for child1Ind, child2Ind in zip(range(0,len(pop),2), range(1,len(pop),2)):
			if(np.random.uniform() < cxPb):
				# set species so you know which result corresponds to each parent
				pop[child1Ind].species = 1
				pop[child2Ind].species = 2
				
				# create a deep copy for the newly mutated individuals
				ch_1 = copy.deepcopy(pop[child1Ind])
				ch_2 = copy.deepcopy(pop[child2Ind])
				new_inds = toolbox.mate(ch_1, ch_2)
				
				# add new mutants to the mutants list
				mutants.append(new_inds[0])
				mutants.append(new_inds[1])
				'''
				# assign fitness to new individuals
				for new_ind in new_inds:
					output = toolbox.evaluate(new_ind)
					output_tup = (new_ind, output, PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
						np.array([[]]), np.array([[]]), 1)
					fit = toolbox.assign_fit(output_tup)
					new_ind.fitness.values = fit
	
				# find if the mutants are more fit than parents
				for child in new_inds:
					other_ind = pop[child1Ind] if pop[child1Ind].species == child.species else pop[child2Ind]
					if(child.fitness.dominates(other_ind.fitness)):
						dom_good += 1
					elif(other_ind.fitness.dominates(child.fitness)):
						dom_bad += 1
					else:
						non_dom += 1
				'''
		# assign fitnesses to all mutants in the mutants list
		# only the output pixels are mapped back, all evaluation must be done below
		outputs = list(toolbox.map(toolbox.evaluate, mutants))

                # create full matrices of archived and current vectors
		full_pop_vecs = np.vstack(outputs)
		# only create the archive vectors if there are individuals in the archive
		if(len(NOV_ARCHIVE) > 0):
			# must grab the numpy arrays out of each tuple in novelty archive
			full_archive_vecs = np.vstack([x[1] for x in NOV_ARCHIVE])
		else:
			full_archive_vecs = np.array([[]])

		# create tuples that can be fed into the novelty fitness assignment function
		output_tups = [(gen, vec[0], PIXELS, 1.0, MATERIAL_PENALIZATION_THRESHOLD, MATERIAL_UNPRESENT_PENALIZATION,
			full_pop_vecs, full_archive_vecs, K_VAL) for gen, vec in zip(mutants, outputs)]

		# map all outputs to the genotypes with their actual fitness assigned
		fitnesses = list(toolbox.map(toolbox.assign_fit, output_tups))

		# find all output lists that should be added to the archive
		for index in range(len(fitnesses)):
			# randomly add individuals into the archive based on a probability
			if(np.random.uniform() <= ARCHIVE_PROB):
				NOV_ARCHIVE.append((mutants[index], outputs[index]))

		org_ind = 0
		for f,o in zip(fitnesses, outputs):
			gen = mutants[org_ind]
			gen.fitness.values = f
			org_ind += 1

			'''
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
			
			'''
		# print domination info after mutation
		#total = dom_good + dom_bad + non_dom + 0.0
		#print("Mutants dominate parents: " + str(dom_good/total))
		#print("Parents dominate mutants: " + str(dom_bad/total))
		#print("Parents/mutants don't dominate:" + str(non_dom/total))

		# select individuals to be present in the next generation's population
		pop = toolbox.select(pop + mutants, k=POP_SIZE)
		
		# must clear the dictionary of innovation numbers for the coming generation
		# only check to see if same innovation occurs twice in a single generation
		gb.clearDict()
		
		# save the population if it has reached a saving point in the evolution
		if(g > 0 and g % NGEN_TO_SAVE == 0):
			file_name = get_file_name("/home/crwolfe/Documents/CPPN_test_env/CPPN_pop_result", "CPPN_quick_test".format(str(g)))
			save_population(pop, SEED, file_name)				



	# return the population after it has been evolved
	return pop



# runs the main evolutionary loop if this file is ran from terminal
if __name__ == '__main__':
	'''
	# open all of the tuples
	gen_list = [str(i) for i in range(5,9)]	
	

	all_pops = [pickle.load(open("/home/wolfecameron/Desktop/CPPN_pop_result/CPPN_parameter_test{0}.txt".format(gen), "rb"))[0] for gen in gen_list]
	all_pars = [get_pareto_front(pop) for pop in all_pops]
	for x in all_pars:
		print(len(x))
	colors = get_n_colors(N=len(gen_list))
	plot_pareto_front(all_pars, ['r', 'y', 'b', 'm'], gen_list)

	pop = []
	par = all_pars[2]
	for ind in par:
		tup = ind.fitness.values
		if(3500 <= tup[0] <= 6000 and 10 <= tup[1] <= 200):
			pop.append(ind)
	
	print(len(pop))
	input()
	#pop = pop[200:]
	index = 0
	for individual in pop:
		print("plotting individual {0}".format(str(index)))
		org = Genotype(2,1)
		org.connections = individual.connections
		org.nodes = individual.nodes
		org.gSize = individual.gSize
		output = []
		for ins in NORM_IN:
			output.append(org.getOutput(ins)[0])
		graphImage(np.array(output, copy=True), NUM_X, NUM_Y, 200)
		org.graph_genotype()
		index += 1
	
	'''
	# the following are all parameter settings for main function
	NGEN = args.ngen
	WEIGHT_MUTPB = .3#float(args.weight)/100.0 #.3 
	NODE_MUTPB = .03#float(args.node)/100.0 #.02
	CON_MUTPB = .15#float(args.con)/100.0 #.1
	CXPB = .1#float(args.cross)/100.0 #.1
	ACTPB = .1#float(args.act)/100.0 #.05
	THRESHOLD = 3.0
	ALPHA = 1.0
	THETA1 = 1.0
	THETA2 = 1.0
	THETA3 = 0.4
	NUM_IN = 2
	NUM_OUT = 1

	# run main EA loop
	finalPop = main(NGEN, WEIGHT_MUTPB, NODE_MUTPB, CON_MUTPB, CXPB, ACTPB, THRESHOLD, ALPHA, THETA1, THETA2, THETA3, NUM_IN, NUM_OUT)
