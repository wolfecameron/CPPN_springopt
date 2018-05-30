'''
The following file contains functions that are used to extract needed pixel 
data from any photo that may be used in experiment with CPPN. 

These pixels can be extracted from an image and converted to binary based on 
the greyscale version of the image
'''
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors



'''
method for retrieving pixels from a given image
original image is resized and the pixels from the image
are returned in a numpy array
@param filepath the filepath to the picture being read
@param numX the width of the resized photo 
@param numY the heigh of the resized photo
@return pixels from resized photo in a list
'''
def getPixels(filepath, numX,numY):
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
	im.show()
	input("Is this the correct image?")

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


# used for quick simple testing of functions
if __name__ == '__main__':
	X = 50
	Y = 50
	file = '/home/wolfecameron/Desktop/CPPN_to/Images/spring9.png'
	pix = getPixels(file, X, Y)
	bin_pix = convertBinary(pix)
	graphImage(bin_pix, X, Y)