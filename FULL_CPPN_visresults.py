'''Creates entire deap configuration and environment that is needed to examine
CPPN results that were evolved using DEAP - configures all DEAP information and
then contians functions to visualize results in certain ways'''

import pickle

# all deap configuration is created when you import the file
from FULL_CPPN_deapconfig import get_tb
from FULL_CPPN_struct import Genotype
from FULL_CPPN_vis import plot_pareto_front
from FULL_CPPN_getpixels import graphImage

# get toolbox from deap config in case it is needed
toolbox = get_tb()


def load_pops(filepaths):
	"""takes a list of filepaths and loads in all associated
	results populations that are stored in the serialized
	files at these locations
	"""
	
	pops = []
	# append every desired population into the list
	for fp in filepaths:
		# must take the 0th element because seed stored @ index 1
		curr_pop = pickle.load(open(fp, "rb"))[0]
		pops.append(curr_pop)

	return pops	

def trim_par_front(par_frnt, func):
	"""takes a pareto front as an input and selects all
	individuals that cause func to return true and returns
	them in a separate list - used to find the elbow of
	the pareto optimal set usually
	"""
	
	return [f for f in par_frnt if func(f)]

def view_results(pop, num_x, num_y):
	"""Method that plots the genotype and phenotype of
	all individuals in pop sequentially
	"""        
	
	# must load input to get ouput from the CPPN
	NORM_IN = pickle.load("norm_in.txt", "rb") 

	counter = 0 # use to print index to terminal
	for ind in pop:
		print("Plotting Individual {0}".format(str(counter)))
		
		# instantiate a new genotype that can be used to replicate result individual
		# because results were in pickle file they lost all class methods
		org = Genotype(NUM_IN, NUM_OUT)
		org.connections = ind.connections
		org.nodes = ind.nodes
		org.gSize = ind.gSize
		
		# get CPPN output
		output = []
		for ins in NORM_IN:
			output.append(org.getOutputs(ins)[0])
		graphImage(np.array(output), num_x, num_y, 200)
		
		# graph genotype of individual after graphing phenotype
		org.graph_genotype()
		counter += 1

if __name__ == '__main__':
	"""Main method - used to actual view results"""

