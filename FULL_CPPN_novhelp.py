"""This file contains all extra helper functions that must be used for
the novelty search algorithm with the evolution of a CPPN, the majority
of the functions are utilized in the FULL_CPPN_novelty ea file
"""

import numpy as np


def get_euclid_dist(vec_1, vec_2):
	"""Method for calculating the euclidian distance of
	vectors using numpy
	"""

	return np.sqrt(np.sum(np.square(vec_1 - vec_2), axis=1)).flatten()

def get_kNN_measure(curr_vec, pop_vecs, archive_vecs, k):
	"""Method for finding the k nearest distances between the current
	result vector and all existing result vectors in the population
	and archive of novel individuals.

	pre -- archive_vecs should be null if there are no archive vectors yet
	"""

	# vectorize this computation to do it all at once
	# each row of pop_vecs should be an output/phenotype
	pop_vec_dist = get_euclid_dist(curr_vec, pop_vecs)
	if(archive_vecs != None):	
		archive_vec_dist = get_euclid_dist(curr_vec, archive_vecs)
		# sort the distances and take the top k for average
		all_dist = sorted(np.concatenate((pop_vec_dist, archive_vec_dist)))
	else:
		all_dist = pop_vec_dist

	# return average of the k smallest distances
	return (np.mean(all_dist[:k]),)




if __name__ == "__main__":
	"""Used for quick testing for compile errors"""

	x = [np.array([0,1,1,1]), np.array([0,1,1,1]), np.array([0,1,1,1])]
	x = np.vstack((x))
	y = [np.array([1,1,1,1]), np.array([0,0,1,1])]
	y = np.stack((y))
	print(x)
	print(y)

	nn = get_kNN_measure(np.array([[0,0,1,1]]), x, y, 2)
	print(nn)