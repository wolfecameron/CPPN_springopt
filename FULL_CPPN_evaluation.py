'''
This file contains all different evaluation functions that
are used for different evolution experiments

These functions can be plugged in to the main deap ea to 
configure the evolution toward whatever experiment is being run
'''
import numpy as np

from FULL_CPPN_scoop import get_all_outputs_scoop


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

def evaluate_xor_scoop(individual, speciesLength):
	"""Same function as the one above but it uses 
	scoop to obtain the entire output of the CPPN
	in parallel
	"""

	inputs = [(individual, [0,0]), (individual, [1,0]), (individual, [0,1]), (individual, [1,1])]
	expectedOutputs = [0,1,1,0]
	actualOutputs = get_all_outputs_scoop(inputs)
	print(actualOutputs)
	input()
	fitness = 0.0
	# find niche count of first row and then delete first row
	#nicheCount = np.sum(nicheCounts[row])
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i][0])**2)
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
		diff = abs(d[2] - output)
		if(diff <= .3):
			numSuccessfulTrials += 1

	return (numSuccessfulTrials/speciesLength),

'''
fitness evaluation for evolving a CPPN based on a picture
@param individual the organism for which the species is being evaluated
@param pixels the binary values for the pixels that were taken from the picture in a numpy array
@param normIn the list of normalized inputs of the (x,y) locations in the picture
@param speciesLength the size of a species for the given individual
@param material_penalization_threshold any solution using less than this proportion of material
will be penalized
@return fitness as a single value in a tuple
'''
def evaluate_pic(individual, pixels, normIn, speciesLength, material_penalization_threshold):
	# penalizes CPPN extra for not putting a material in a place 
	# that has material in original picture, this is needed because
	# there are significantly fewer locations with pixels than without generally	
	NO_MATERIAL_PENALIZATION = 3	

	outputs = []
	# get all outputs for every pixel in space of picture and put all into a numpy array
	for ins in normIn:
		outputs.append(individual.getOutput([ins[0], ins[1]])[0])

	# convert outputs to a numpy array
	outputs_np = np.array(outputs, copy = True)

	# decide if fitness should be penalized for using too little material
	total_px_used = float(np.sum(outputs_np))
	penalization = 1.0
	proportion_mat_used = total_px_used / (len(pixels))
	if(proportion_mat_used <= material_penalization_threshold):
		# penalization starts at dividing by 2 and becomes larger as less material used
		# the + .001 is included to avoid dividing by 0
		penalization = 2.0 * (material_penalization_threshold / (proportion_mat_used + .001))
	
	# find difference between CPPN output and target by subtracting and 
	# squaring the two arrays, then finding the sum of the resultant array
	# subtract the difference from 1 because we are maximizing fitness
	ones_arr = np.ones((1, len(pixels)))
	diff = np.subtract(pixels, outputs_np)
	diff[diff>=.5] *= NO_MATERIAL_PENALIZATION
	diff = np.absolute(diff)
	total_fit = np.sum(np.subtract(ones_arr, diff))

	# account for species sharing and material penalization into the returned fitness
	return (total_fit/(speciesLength*penalization),)


