'''
This file contains all different evaluation functions that
are used for different evolution experiments

These functions can be plugged in to the main deap ea to 
configure the evolution toward whatever experiment is being run
'''
import numpy as np

'''
fitness evaluation used for DEAP CPPN XOR implementation
@params individual the organism that is currently being evaluated
@param speciesLength the number of individuals in the species for the given individual
@return fitness of individual in a tuple
'''
def evaluate_xor(individual, speciesLength):
	# store inputs and actual/expected values in same order in lists 
	inputs = [[0,0], [1,0], [0,1], [1,1]]
	expectedOutputs = [0,1,1,0]
	actualOutputs = []
	# get output of individual for all different inputs
	for values in inputs:
		actualOutputs.append(individual.getOutput(values)[0])
	fitness = 0.0
	# find niche count of first row and then delete first row
	#nicheCount = np.sum(nicheCounts[row])
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i])**2)
	# square the resulting fitness	
	fitness = fitness**2

	return (fitness/speciesLength),


'''
fitness evaluation function for the data set classification tests for CPPN
@param individual the individual CPPN for which the fitness is being found
@param speciesLength number of individuals in the species for the individual being evaluated
@param dataSet the data set for which the CPPN is being trained/tested
@return the fitness for the given CPPN as a single value inside of a tuple
'''
def evaluate_classification(individual, speciesLength, dataSet):
	# store the number of successful data points and return it
	numSuccessfulTrials = 0.0
	for d in dataSet:
		# find difference in actual and desired output, trial is succesful if difference less than .5
		output = individual.getOutput([d[0], d[1]])[0]
		diff = np.fabs(d[2] - output)
		if(diff <= .5):
			numSuccessfulTrials += 1

	return (numSuccessfulTrials/speciesLength),


