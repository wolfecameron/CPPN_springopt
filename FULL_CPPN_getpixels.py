'''
The following file contains functions that are used to extract needed pixel 
data from any photo that may be used in experiment with CPPN. This file also
contains the function for creating the inputs needed for CPPN structure evolutions. 

These pixels can be extracted from an image and converted to binary based on 
the greyscale version of the image
'''
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import sys


'''
THIS IS THE MAIN METHOD THAT SHOULD BE USED FOR GRABBING PIXELS IN OTHER FILES
method for getting numpy array of binary pixels that is used
in fitness evaluation for CPPN
@param filepath path to image file that CPPN is being compared to 
@param numX width of picture in pixels
@param numY height of picuture in pixels
@return numpy array containing all binary pixel values from original picture
'''
def getBinaryPixels(filepath, numX, numY):
	# gets normal RGB pixels in a list and converts to a numpy array of binary pixels
	rgb_pix = getRGBPixels(filepath, numX, numY)
	bin_pix = convertBinary(rgb_pix)

	return bin_pix

'''
method for retrieving pixels from a given image
original image is resized and the pixels from the image
are returned in a numpy array
@param filepath the filepath to the picture being read
@param numX the width of the resized photo 
@param numY the heigh of the resized photo
@return pixels from resized photo in a list
'''
def getRGBPixels(filepath, numX,numY):
	# declare prefered size of image
	SIZE = (numX,numY)

	# open image from its source file (original size)
	try:
		im_tmp = Image.open(filepath)
	except:
		#if image cannot open, function exits
		print("ERROR(getPixels): File Path not valid.")
		return

	#resizes image to preferred size
	im = im_tmp.resize(SIZE)

	# create a list containing tuples of pixels from resized image
	pixels = list(im.getdata())

	return pixels


'''
takes in a list of rgb pixels and converts it to a 
numpy array of binary pixels 
@param pixels list of rgb pixels
@return numpy array containing binary version of rgb pixels
pre: pixels should only contain completely black and white pixels
'''
def convertBinary(pixels):
	# any pixel above binary threshold considered white, vic versa
	BINARY_THRESHOLD = 200
	binList = []

	# only the first value in the tuple can be observed
	# these values will never be different because spring images
	# are already black and white
	for x in pixels:
		# value of 255 is white, value of 0 is black
		# 255 -> 0, 0 -> 1
		if(x[0] > BINARY_THRESHOLD):
			binList.append(0)
		else:
			binList.append(1)

	# return numpy version of binary pixel array
	return np.array(binList, copy = True)


'''
creates a graph of an image represented by a list of binary pixels
@param binPixels the numpy array containing binary pixels for image
@param numX width of the picture represented by pixels
@param numY height of picture represented by pixels
pre: length of binPixels and numX*numY must match
pre: binPixel IS A NUMPY ARRAY
'''
def graphImage(binPixels, numX, numY, fig_num):
	# check precondition
	if(not len(binPixels) == numX*numY):
		print("Length of pixel list and given size do not match!")
		return 0

	# create 2D picture representation of pixels with matplotlib
	#plt.ion()
	plt.figure(fig_num)
	im = plt.imshow(-binPixels.reshape(numX, numY), cmap='gray', interpolation='none', norm=colors.Normalize(vmin=-1, vmax=0))
	# must include an input or figures will open continuously an cause stack overflow
	#input()

'''
This function generates the inputs for the CPPN that are used in 
modeling a 2D picture/structure
@param numX the width of the 2D space in px
@param numY the height of the 2D space in px
@return a list of normalized input values for the CPPN
'''
def getNormalizedInputs(numX, numY):
	# find mean and std for x and y values in inputs, same for both x and y
	tmp = np.array([x for x in range(1, numX + 1)], copy = True)
	MEAN = np.mean(tmp)
	STD = np.std(tmp)

	#list of normalized inputs
	normIn = [] 

	#creates input list with normalized vectors, values of input are of form (x,y) in a list of tuples
	for y in range(0,numY):
		for x in range(0,numX):
			tup = ((x - MEAN)/STD, (y-MEAN)/STD)
			normIn.append(tup)

	return normIn



def get_d_mat(pixels, numX, numY):
	"""Generates the matrix that contains all values for 
	the distance parameter that will be used in CPPN
	activation.
	"""

	result = np.zeros((numX, numY))
	px = np.reshape(pixels, (numX, numY))

	zeros = []
	ones = []

	# populate all positions of ones and zeros into the above list
	# for distance calculations
	for r in range(px.shape[0]):
		for c in range(px.shape[1]):
			if px[r][c] == 1:
				ones.append((r, c))
			else:
				zeros.append((r, c))

	# perform distance calculations on all positions and find minimum
	# distance for each position in the matrix
	for r in range(px.shape[0]):
		for c in range(px.shape[1]):
			shortest_dist = sys.maxsize
			if px[r][c] == 1:
				for pos in zeros:
					tmp_dist = get_distance((r, c), pos)
					if tmp_dist < shortest_dist:
						shortest_dist = tmp_dist
			else:
				for pos in ones:
					tmp_dist = get_distance((r, c), pos)
					if tmp_dist < shortest_dist:
						shortest_dist = tmp_dist
			# d should be negative if the pixel has a value of 0
			result[r][c] = shortest_dist if px[r][c] == 1 else -shortest_dist



			
	
	# flatten result before return to make it same form as 
	# the other normalized location inputs
	return result#.flatten()


def get_distance(tup_1, tup_2):
	"""Method for finding the euclidian distance between two positions
	in a matrix"""

	diff = np.square((tup_1[0] - tup_2[0])) + np.square((tup_1[1] - tup_2[1]))
	return np.sqrt(diff)

'''
def _get_opp_dist(px, r, c, numX, numY):
	"""Function that calls the recursive method to find
	the number of pixels between the current and a different
	color of pixel.
	"""

	return _helper(px, r, c, px[r][c], numX, numY)

def _helper(px, r, c, og, numX, numY):
	"""Recursive method for finding the distance from the current pixel
	to a pixel of a different color. 
	"""

	if(not check_bounds(px, r, c) or px[r][c] == -1):
		return numX*numY + 1
	elif(px[r][c] != og):
		return 0

	# track which spaces you have been to
	old_value = px[r][c]
	px[r][c] = -1

	# recurse through each point adjacent to current
	best_count = sys.maxsize
	for x in range(-1, 2):
		for y in range(-1, 2):
			tmp_count = 1 + _helper(px, r + x, c + y, og, numX, numY)
			# find point with smallest number of pixels to a different color pixel
			if(tmp_count < best_count):
				best_count = tmp_count
	
	# undo the change
	px[r][c] = old_value

	return best_count

def check_bounds(px, r, c):
	"""Checks that a certain row and column position
	is within the bounds of the given matrix.
	"""

	return r >= 0 and c >= 0 and r < px.shape[0] and c < px.shape[1]
'''
# used for quick simple testing of functions
if __name__ == '__main__':
	"""
	X = 50
	Y = 50
	file = '/home/wolfecameron/Desktop/CPPN_springopt/fitting_images/heart_ex.png'
	bin_pix = getBinaryPixels(file, X, Y)
	graphImage(bin_pix, X, Y, 100)
	plt.show()
	input()
	"""

	curr_mat = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
	print(np.reshape(curr_mat, (3,4)))
	x = get_d_mat(curr_mat, 3, 4)
	print(x)
