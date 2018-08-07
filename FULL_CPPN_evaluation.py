'''
This file contains all different evaluation functions that
are used for different evolution experiments

These functions can be plugged in to the main deap ea to 
configure the evolution toward whatever experiment is being run
'''
import numpy as np
import pickle

from FULL_CPPN_scoop import activate_CPPN_scoop
from FULL_CPPN_getpixels import getNormalizedInputs
from FULL_CPPN_novhelp import get_kNN_measure
from FULL_CPPN_disthelp import get_hausdorff_dist

'''
fitness evaluation used for DEAP CPPN XOR implementation
@params genotype the organism that is currently being evaluated
@param speciesLength the number of genotypes in the species for the given genotype
@return fitness of genotype in a tuple
'''
def evaluate_xor(genotype, speciesLength):
	# store inputs and actual/expected values in same order in lists 
	inputs = [[0,0], [1,0], [0,1], [1,1]]
	expectedOutputs = [0,1,1,0]
	actualOutputs = []
	# get output of genotype for all different inputs
	for values in inputs:
		actualOutputs.append(genotype.getOutput(values)[0])
	fitness = 0.0
	# find niche count of first row and then delete first row
	#nicheCount = np.sum(nicheCounts[row])
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i])**2)
	# square the resulting fitness	
	fitness = fitness**2

	return (fitness/speciesLength),

def evaluate_xor_scoop(genotype):
	"""Same function as the one above but it uses 
	scoop to obtain the entire output of the CPPN
	in parallel
	"""

	# store inputs and actual/expected values in same order in lists 
	inputs = [[0,0], [1,0], [0,1], [1,1]]
	expectedOutputs = [0,1,1,0]
	actualOutputs = []
	# get output of genotype for all different inputs
	for values in inputs:
		actualOutputs.append(genotype.getOutput(values)[0])
	fitness = 0.0
	# find niche count of first row and then delete first row
	#nicheCount = np.sum(nicheCounts[row])
	for i in range(len(expectedOutputs)):
		# return the 1 - the difference so that fitness can be maximized
		fitness += (1 - (expectedOutputs[i] - actualOutputs[i])**2)
	# square the resulting fitness	
	fitness = fitness**2

	return (fitness),



'''
fitness evaluation function for the data set classification tests for CPPN
@param genotype the genotype CPPN for which the fitness is being found
@param speciesLength number of genotypes in the species for the genotype being evaluated
@param dataSet the data set for which the CPPN is being trained/tested
@return the fitness for the given CPPN as a single value inside of a tuple
'''
def evaluate_classification(genotype, speciesLength, dataSet):
	# store the number of successful data points and return it
	numSuccessfulTrials = 0.0
	for d in dataSet:
		# find difference in actual and desired output, trial is succesful if difference less than .5
		output = genotype.getOutput([d[0], d[1]])[0]
		diff = abs(d[2] - output)
		if(diff <= .3):
			numSuccessfulTrials += 1

	return (numSuccessfulTrials/speciesLength),

'''
fitness evaluation for evolving a CPPN based on a picture
@param genotype the organism for which the species is being evaluated
@param pix the binary values for the pix that were taken from the picture in a numpy array
@param normIn the list of normalized inputs of the (x,y) locations in the picture
@param speciesLength the size of a species for the given genotype
@param material_penalization_threshold any solution using less than this proportion of material
will be penalized
@return fitness as a single value in a tuple
'''
def evaluate_pic(genotype, pix, normIn, speciesLength, material_penalization_threshold):
	# penalizes CPPN extra for not putting a material in a place 
	# that has material in original picture, this is needed because
	# there are significantly fewer locations with pix than without generally	
	NO_MATERIAL_PENALIZATION = 3	

	outputs = []
	# get all outputs for every pixel in space of picture and put all into a numpy array
	for ins in normIn:
		outputs.append(genotype.getOutput([ins[0], ins[1]])[0])

	# convert outputs to a numpy array
	outputs_np = np.array(outputs, copy = True)

	# decide if fitness should be penalized for using too little material
	total_px_used = float(np.sum(outputs_np))
	penalization = 1.0
	proportion_mat_used = total_px_used / (len(pix))
	if(proportion_mat_used <= material_penalization_threshold):
		# penalization starts at dividing by 2 and becomes larger as less material used
		# the + .001 is included to avoid dividing by 0
		penalization = 2.0 * (material_penalization_threshold / (proportion_mat_used + .001))
	
	# find difference between CPPN output and target by subtracting and 
	# squaring the two arrays, then finding the sum of the resultant array
	# subtract the difference from 1 because we are maximizing fitness
	ones_arr = np.ones((1, len(pix)))
	diff = np.subtract(pix, outputs_np)
	diff = np.absolute(diff)
	total_fit = np.sum(np.subtract(ones_arr, diff))

	# account for species sharing and material penalization into the returned fitness
	return (total_fit/(speciesLength*penalization),)


def evaluate_pic_scoop(genotype):
	"""simplified version of picture evaluation function that is compatible
	with scoop, previous version could not be pickled with all parameters
	"""

	NUM_X = 75
	NUM_Y = 75
	NORM_IN = pickle.load(open("norm_in.txt", "rb"))
	output = []
	# get all outputs and append them to output list
	for ins in NORM_IN:
		ins = (genotype, ins)
		result = activate_CPPN_scoop(ins)[0]
		output.append(result)
	
	return (np.array(output, copy=True),)


def assign_fit_scoop(info_tup):
	"""Takes tuple containing an output array of pix
	and all info needed to calculate associate fitness 
	and returns a genotype object with this fitness assigned
	to it.

	Parameters:
	info_tup -- contains output pix, genotype, target pix, 
	and all needed constants for fitness calculation
	"""

	# get all needed info out of the tuple
	out, pix, spec_len, mat_pen, mat_unp = info_tup

	# compute fitness, penalizing for material used
	proportion_mat_used = float(np.sum(out))/len(pix)
	penalization = 1.0
	if(proportion_mat_used <= mat_pen):
		penalization = 2.0 * (mat_pen / (proportion_mat_used + .001))
	
	# find difference between the two pixel arrays
	ones_arr = np.ones((1, len(pix)))
	diff = np.subtract(pix, out)
	diff[diff>=.5] *= mat_unp
	diff = np.fabs(diff)
	total_fit = (np.sum(np.subtract(ones_arr, diff)))/(spec_len*penalization)

	return (total_fit,)

def evaluate_pic_dparam(genotype):
	"""simplified version of picture evaluation function that is compatible
	with scoop, this version also activates the CPPN with the use of the d
	parameter derived from the pixels in the target image.
	"""

	NUM_X = 50
	NUM_Y = 50
	NORM_IN = pickle.load(open("norm_in.txt", "rb"))
	D_MAT = pickle.load(open("d_mat.txt","rb"))
	output = []
	# get all outputs and append them to output list
	for (ins_1, ins_2) in zip(NORM_IN, D_MAT):
		ins_tup = (ins_1[0], ins_1[1], ins_2)
		ins = (genotype, ins_tup)
		result = activate_CPPN_scoop(ins)[0]
		output.append(result)
	
	return (np.array(output, copy=True),)

def evaluate_novelty(eval_tup):
	"""Evaluation function for the novelty search evolutionary
	algorithm with CPPN - calls the function in novelty help that
	determines a solution's distance from another
	"""

	# must unpack all items from the tuple parameter
	curr_vec, pop_vec, archive_vec, k = eval_tup

	return get_kNN_measure(curr_vec, pop_vec, archive_vec, k)

def evaluate_nov_pic(eval_tup):
	"""Method for evaluating novelty and closeness to a target
	picture simulatanously - individuals then selected with the
	use of NSGA-II"""
	
	# unpack the input tuple
	genotype, output, black_dist, white_dist = eval_tup
	
	# get fitness for both objectives	
	target_fit = get_hausdorff_dist(output, black_dist, white_dist)#assign_fit_scoop((output, pixels, spec_len, mat_pen, mat_unp))
	con_fit = (len(genotype.connections), )#evaluate_con_cost(genotype)#evaluate_novelty((output, pop_vec, archive_vec, k))

	# return fitness for both objectives inside of a tuple
	return (target_fit[0], con_fit[0])

def evaluate_con_cost(genotype):
	"""Evaluates the connection cost fitness of a given network
	using the connection cost class method.
	"""

	return genotype.get_con_cost(),
