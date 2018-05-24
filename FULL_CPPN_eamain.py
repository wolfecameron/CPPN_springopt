from FULL_CPPN_struct import Genotype
from FULL_CPPN_evalg import binarySelect, tournamentSelect, applyWeightMutation, applyConMutation, applyNodeMutation
from FULL_CPPN_evalg import applyCrossover, evaluateFitness, evaluateFitness_fitsharing, evaluateFitness_nichecount, getFittestFromSpecies
from FULL_CPPN_vis import visHiddenNodes, visConnections, findNumGoodSolutions
import matplotlib.pyplot as plt
import numpy as np

'''
This file contains the main driver for the evolutionary algorithm of CPPN
it uses functions from FULL_CPPN_evalg.py to select and mutate the population
final individuals are returned after the evolutionary algorithm is completed
'''

# following lists used to track data as the main function runs
AVERAGE_FITNESSES = []

'''
main function that runs the evolutionary algorithm
@param numIn the number of inputs into the original genotype
@param numOut the number of outputs from the original genotype
@param numGen the number of generations the evolution is run
@param popSize the number of individuals in each population
@param cxpb the probability of crossover
@param mutpb the probability of mutation
@return the final population after EA is completed
'''
def main(numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb):
	# always maintain a global state of all existing connections innov nums
	globalInnovation = ((numIn + 1) * numOut) + 1
	pop = []
	for loop in range(popSize):
		pop.append(Genotype(numIn, numOut))
	
	### ***** MAIN EA LOOP ***** ###
	for g in range(numGen):
		print("RUNNING GENERATION " + str(g))
		# evaluate function handles speciation of population
		if(g == 145):
			visHiddenNodes(pop)
		THRESHOLD = 3.0
		THETA1 = 1.0
		THETA2 = 1.0
		THETA3 = 0.4
		tournSize = 3
		evaluationTup = evaluateFitness_nichecount(pop, THRESHOLD, THETA1, THETA2, THETA3, g)
		species = evaluationTup[0]
		print(len(species))
		AVERAGE_FITNESSES.append(evaluationTup[1])
		#print(len(species))
		popTup = getFittestFromSpecies(species)
		partialPop = popTup[0]
		pop = popTup[1]
		pop = binarySelect(pop, partialPop)
		# always apply mutation and crossover after selection
		applyWeightMutation(pop, weight_mutpb)
		globalInnovation = applyConMutation(pop, con_mutpb, globalInnovation)
		globalInnovation = applyNodeMutation(pop, node_mutpb, globalInnovation)
		#pop = applyCrossover(pop, cxpb)
	
	# return the resultant population after evolution done
	return pop#findFittest(pop)

'''
method for finding fittest individual in a population
@return the individual within pop with the best fitness
'''
def findFittest(pop):
	bestInd = None
	for org in pop:
		if(bestInd == None or bestInd.getFitness() < org.getFitness()):
			bestInd = org
	
	return bestInd 

'''
prints xor results for each individual of the final population
used to determine how the CPPN performed
@param pop the population that was created during evolution
'''
def printResultingInds(pop):
	for ind in pop:	
		if(ind.getHiddenNodes() > 0):
			print(ind.getOutput([0,0])[0])
			print(ind.getOutput([0,1])[0])
			print(ind.getOutput([1,0])[0])
			print(ind.getOutput([1,1])[0])
			input("View next by hitting anything.")

'''
creates a line graph of average fitnesses throughout evolution
used to determine performance of the CPPN
'''
def plotFitnessResults(fitnesses):
	plt.plot(AVERAGE_FITNESSES)
	plt.title("XOR - CPPN")
	plt.ylabel("Average Fitness")
	plt.xlabel("Generation")
	plt.show()




# main function for running EA
if __name__ == "__main__":
	# order of parameters for main : (numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb)
	numIn = 2
	numOut = 1
	numGen = 150
	popSize = 150
	weight_mutpb = .35
	con_mutpb = .1
	node_mutpb = .02
	cxpb = .1
	pop = main(numIn, numOut, numGen, popSize, weight_mutpb, con_mutpb, node_mutpb, cxpb)
	xor_result = findNumGoodSolutions(pop)
	print("Number of Good Solutions: " + str(xor_result[0]))
	print("Number of Bad Solutions: " + str(xor_result[1]))
	printResultingInds(pop)
	plotFitnessResults(AVERAGE_FITNESSES)