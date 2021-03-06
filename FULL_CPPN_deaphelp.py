'''
This file contains all helper functions for the evolutionary algorithm
created using DEAP in the _deapea py file. 

These functions are used to register mutations functions within the 
DEAP framework
'''

import sys
import os

import numpy as np
import pickle

from FULL_CPPN_struct import Genotype
from FULL_CPPN_getpixels import graphImage

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
	
	# set probability for adding new connection or deleting one
	p_add_con = 1.0
	if(np.random.uniform() <= p_add_con):
		globalInnovation.current = individual.connectionMutate(innovResult)
	else:
		individual.connection_status_mutate()

	return  individual,

''' 
method for applying an activation mutation in an individual 
@param individual the individual that is being mutated
@return the individual in the form of a tuple
'''
def actMutate(individual):
	# just use mutation function built into the genotype class
	individual.activationMutate()

	return individual,


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
@param individua1,2 the individuals that are being crossed over
@return child and parent ind resulting from the crossover
'''
def xover(individual1, individual2):
	# cross individuals over and return both new individuals
	(newInd1, newInd2) = individual1.crossoverReturnBoth(individual2)

	return (newInd1, newInd2)

'''
same as above exepct instead of using the regular crossover function 
the average crossover function is used
@param individual1,2 the individuals being crossed over
@return child and parent ind resulting from the crossover
'''
def xover_avg(individual1, individual2):
	# cross individuals over
	(newInd1, newInd2) = individual1.crossoverAvg(individual2)

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
	index = np.random.randint(0, len(partialPop) - 1)
	# continually add copies of individuals for the partial population
	# until partial population is of the correct size
	while(len(partialPop) < popSize):
		currentOrg = partialPop[index % ogSize].getCopy()
		currentOrg.species = sys.maxsize
		partialPop.append(currentOrg)
		index += 1

	return partialPop

'''
activates a CPPN over a range of values and appends all outputs
into an array which can then be used to create a heatmap of the CPPN
output, used to visualize results of data set problems for CPPN
@param org the CPPN that is being activated
@param maxValue the maximum value within the CPPNs range of activation
@param step the distance between successive activations of the CPPN
@return numpy array containing all outputs that is resized properly to be put into the heat map
'''
def getOutputsForHeatMap(org, maxValue, step):
	outputs = []
	# start activating at upper left corner of range
	# move down the column of pixels then move to the next row
	# until the bottom right corner is reached
	xVal = -maxValue
	while(xVal <= maxValue):
		yVal = maxValue
		while(yVal >= -maxValue):
			outputs.append(org.getOutput([xVal, yVal])[0])
			yVal -= step
		xVal += step

	# put values into a numpy array and reshape it based on maxValue and step before returning
	outputs_np = np.array(outputs, copy = True)
	outputs_np = np.reshape(outputs_np, (int(maxValue*2/step), int(maxValue*2/step)))
	return outputs_np


def save_population(population, seed_num, filepath):
	"""Fucntion for serializing an entire population of CPPN
	genotypes using pickle. 

	Parameters:
	population -- the population being saved
	seed_num -- the seed number used to evolve the population
	filename -- the filepath to the file being saved
	"""

	new_file = open(filepath, "wb")
	# save population in a tuple with the seed number
	pop_tuple = (population, seed_num)
	pickle.dump(pop_tuple, new_file)
	new_file.close()

def get_file_name(dir_path, name_prefix):
	"""Returns a valid file name that can be used to save a 
	population into a given directory (dir_path)
	"""

	file_names = os.listdir(dir_path)
	# build file name and check if present
	name = name_prefix
	n = 1
	found_name = False
	while(not found_name):
		curr_str = name + str(n) + ".txt"
		if(curr_str in file_names):
			n += 1
		else:
			found_name = True

	return dir_path + "/" + name + str(n) + ".txt"


def examine_population(population, norm_in):
	"""Method for graphing each individual in a population
	for examination (Genotype and Phenotype)

	Parameters:
	population -- the population of CPPNs being examined
	norm_in -- input values into CPPN to produce phenotype
	"""

	n = 0
	for org in population:
		outputs = []
		# get all outputs for every pixel in space of picture and put all into a numpy array
		for ins in norm_in:
			outputs.append(org.getOutput([ins[0], ins[1]])[0])
		outputs_np = np.array(outputs, copy = True)
		# 100 and 200 represent the figure numbers for each of the separate graphs
		graphImage(outputs_np, NUM_X, NUM_Y, 100)
		org.graph_genotype(200)
		input("SHOWING individual #{0}".format(str(n)))
		n += 1

def examine_population_dmat(population, NUM_X, NUM_Y):
	"""Method for graphing each individual in a population
	for examination (Genotype and Phenotype) with the d parameter.
	"""

	norm_in = pickle.load(open("norm_in.txt", "rb"))
	d_mat = pickle.load(open("d_mat.txt", "rb"))

	n = 0
	for org in population:
		outputs = []
		# get all outputs for every pixel in space of picture and put all into a numpy array
		for ins_1, ins_2 in zip(norm_in, d_mat):
			ins = (ins_1[0], ins_1[1], ins_2)
			outputs.append(org.getOutput(ins)[0])
		outputs_np = np.array(outputs, copy = True)
		# 100 and 200 represent the figure numbers for each of the separate graphs
		graphImage(outputs_np, NUM_X, NUM_Y, 100)
		org.graph_genotype(200)
		input("SHOWING individual #{0}".format(str(n)))
		n += 1

def get_pareto_front(pop):
	"""This function goes through a population and finds the pareto
	optimal front within the population and returns it within a list.
	The pareto optimal front is all individuals that are not dominated
	by any other individuals within the population
	"""
	
	pareto_front = []
	# go through every individual and see if that individual is dominated
	for ind in pop:
		fit_tup = ind.fitness
		other_ind = 0
		found_dom = False
		# compare to every other individual in population
		while(not found_dom and other_ind < len(pop)):
			other_fit = pop[other_ind].fitness
			if(other_fit.dominates(fit_tup)):
				found_dom = True
			other_ind += 1
		# add to pareto front if not dominated
		if(not found_dom):
			pareto_front.append(ind)

	
	# return all non-dominated individuals
	return pareto_front

