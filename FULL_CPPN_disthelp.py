"""This file contains all code used for creating a distance metric between two
images - generally a candidate image and a target image"""


import sys

import numpy as np



def get_dist_mat(targ_pix):
	"""Creates a matrix that finds, for every pixel in the target
	pixel matrix, the euclidian distance to the nearest black pixel
	in the target pixel matrix
	"""
	
	# find location of all black pixels
	one_pixels = get_black_pixels(targ_pix)
	
	# instantiate result matrix with all 0s
	result_mat = np.zeros(targ_pix.shape)
	
	# find length between each possible location and closest black pixel
	for r in range(len(targ_pix)):
		for c in range(len(targ_pix[0])):
			# if px is black then closest distance to black px is 0
			# otherwise find closest distance
			if(targ_pix[r][c] != 1):
				closest = get_closest_point((r, c), one_pixels)
				result_mat[r][c] = closest

	return result_mat


def get_black_pixels(targ_pix):
	"""Method that finds the x,y locations of all black pixels
	in a target image matrix"""
	
	one_pixels = []
	for r in range(len(targ_pix)):
		for c in range(len(targ_pix[0])):
			if(targ_pix[r][c] == 1):
				one_pixels.append((r, c))

	return one_pixels


def get_euclidian_dist(pos, other_pos):
	"""Finds the euclidian distance between two (x, y) distance
	tuples"""

	return np.sqrt(np.square(pos[0] - other_pos[0]) + np.square(pos[1] - other_pos[1]))


def get_closest_point(pos_tup, all_pos):
	"""Finds all euclidian distances between the current row
	and column position (in pos_tup) and every (row, column)
	position tuple in all_pos and returns the closest one
	"""
	
	# initialize closest to be a very large number
	closest = sys.maxsize
	
	# go through all other pixels and find the closest one
	for other in all_pos:
		curr_dist = get_euclidian_dist(pos_tup, other)
		if(curr_dist < closest):
			closest = curr_dist
	
	return closest


if __name__ == '__main__':
	"""Used to run simple tests on methods"""
	x = np.array([[1,0,0,0],[0,1,1,0],[0,0,0,0]])
	print(get_dist_mat(x))
	


