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


'''
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
def graphImage(binPixels, numX, numY):
	# check precondition
	if(not len(binPixels) == numX*numY):
		print("Length of pixel list and given size do not match!")
		return 0

	# create 2D picture representation of pixels with matplotlib
	plt.ion()
	fig,ax = plt.subplots()
	im = ax.imshow(-binPixels.reshape(numX, numY), cmap='gray', interpolation='none', norm=colors.Normalize(vmin=-1, vmax=0))
	fig.show()
	input()

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

# used for quick simple testing of functions
if __name__ == '__main__':
	X = 50
	Y = 50
	file = '/home/wolfecameron/Desktop/CPPN_to/Images/spring9.png'
	getNormalizedInputs(X, Y)