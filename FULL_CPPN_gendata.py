'''
This file is used to generate testing data for CPPN
utilizes algroithms similar to the tensorflow playground that can be 
used for testing the CPPN on classification problems

All data points are stored as (x location, y location, classification)
representing a x,y location in space and a classification of 1 or 0
'''
import random as r
import numpy as np
import matplotlib.pyplot as plt


'''
The following function is used to generate a gaussian data set
the data set has data classified as 0 in the 3rd quadrant and 1 in
the 1st quadrant of a graph within the range x = [-maxValue, maxValue]
and y = [-maxValue, maxValue]
@param size the number of elements included in the dataset 
@maxValue the maximum x and y value a data point can hold
@return a gaussian dataset
'''
def genGaussianData(size, maxValue):
	binaryThreshold = .5
	dataSet = []
	# dataSet must have size == size 
	for it in range(size):
		samp = r.random()
		if(samp < binaryThreshold):
			# all 0s  within x,y = [-maxValue, 0]
			xPos = r.random()*(-maxValue)
			yPos = r.random()*(-maxValue)
			dataSet.append((xPos, yPos, 0))
		else:
			# all 1s within x,y = [0, maxValue]
			xPos = r.random()*maxValue
			yPos = r.random()*maxValue
			dataSet.append((xPos,yPos, 1))
	showData(dataSet)
	return dataSet


'''
The following function generates a circular data set
this dataset is characterized as a circle with a given radius 
at the center of the 2D space containing all 0s and an outer circle containing all 1s
@param size the number of elements included in the dataset
@param innerRadius the radius of the inner circle containing all 0s
@param maxValue the maximum x and y values the data points can hold
@return a circlar dataSet
'''
def genCircularData(size, innerRadius, maxValue):
	dataSet = []
	binaryThreshold = .5
	# generate all data for dataset first, determine its classification later
	for it in range(size):
		xPos = r.uniform(-maxValue, maxValue)
		yPos = r.uniform(-maxValue, maxValue)

		# append new point into the data set with a temporary classification number
		dataSet.append((xPos, yPos, 0))
	
	# go through data set and find actual classification of each point
	for dataInd in range(len(dataSet)):
		xPos = dataSet[dataInd][0]
		yPos = dataSet[dataInd][1]
		radius = np.sqrt(np.square(xPos) + np.square(yPos))
		# try to create a defined divide between 1s and 0s
		if(innerRadius - .4 <= radius <= innerRadius + .4):
			dataSet[dataInd] = (xPos*1.5, yPos*1.5, 1)
		# change classification if outside of inner radius
		elif(radius >= innerRadius):
			# must reassign tuple because tuple is not mutable
			dataSet[dataInd] = (xPos, yPos, 1)
	
	# show data to user before fitting is performed
	showData(dataSet)
	return dataSet

'''
the following function generates an XOR data set
the XOR data set has 1s in the 1st and 3rd quarant
and 0s in the 2nd and 4th quadrant
@param size the size of the data set
@param maxValue the maximum x,y value a point in the data set can have
@return a data set with datum of the form (x, y, class)
'''
def genXORData(size, maxValue):
	dataSet = []
	for it in range(size):
		# generate x and y points for data
		x = r.uniform(-maxValue, maxValue)
		y = r.uniform(-maxValue, maxValue)
		# the following lines of code make sure the divides between 1 and 0 are more defined
		CLOSENESS_THRESH = .25
		PUSH_FACTOR = 5
		if(np.fabs(x) <= CLOSENESS_THRESH):
			x *= PUSH_FACTOR
		if(np.fabs(y) <= CLOSENESS_THRESH):
			y *= PUSH_FACTOR
		# use x and y points to classify the data as 1 or 0
		if((x < 0 and y < 0) or (x > 0 and y > 0)):
			dataSet.append((x, y, 1))
		else:
			dataSet.append((x, y, 0))
	showData(dataSet)
	return dataSet

'''
The following function is used to graph the generated data set 
so that it can be visualized
All 1s appear in red and all 0s appear in blue
'''
def showData(dataSet):
	x_zeros = []
	x_ones = []
	y_zeros = []
	y_ones = []
	# parse data points into appropriate sets
	for d in dataSet:
		if(d[2] == 1):
			x_ones.append(d[0])
			y_ones.append(d[1])
		elif(d[2] == 0):
			x_zeros.append(d[0])
			y_zeros.append(d[1])

	plt.scatter(x_zeros, y_zeros, color = 'b')
	plt.scatter(x_ones, y_ones, color = 'r')
	plt.show()


# used to test data set generated correctly
if __name__ == '__main__':
	SIZE = 100
	INNER_RADIUS = 1.7
	MAX_VALUE = 2.0
	data1 = genGaussianData(SIZE, MAX_VALUE)
	showData(data1)
	data2 = genCircularData(SIZE, INNER_RADIUS, MAX_VALUE)
	showData(data2)
	data3 = genXORData(SIZE, MAX_VALUE)
	showData(data3)

