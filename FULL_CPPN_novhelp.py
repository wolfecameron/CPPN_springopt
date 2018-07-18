"""This file contains all extra helper functions that must be used for
the novelty search algorithm with the evolution of a CPPN, the majority
of the functions are utilized in the FULL_CPPN_novelty ea file
"""

import numpy as np


def get_euclid_dist(vec_1, vec_2):
	"""Method for calculating the euclidian distance of
	two vectors using numpy
	"""

	if(vec_1.shape != vec_2.shape):
		print("The vectors do not have the same size, \
				euclidian distance couldn't be found.")
	else:
		return np.sqrt(np.sum(np.square(vec_1 - vec_2)))


if __name__ == "__main__":
	"""Used for quick testing for compile errors"""

	print(get_euclid_dist(np.array([0,0,1]), np.array([0,1,1])))