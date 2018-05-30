'''
This file contains a lot of helper methods that are used to visualize details of CPPN
These are mostly used for debugging and studying CPPN genotypes
'''
import matplotlib.pyplot as plt

'''
Creates bar graph showing the most common numbers of hidden nodes
shows frequency of each hidden node value in the bar graph
@param pop population for which hidden nodes are being visualized
post: print out a graph to visualize number of hidden nodes in the given population
'''
def visHiddenNodes(pop):
	allHiddenVals = []
	# generate all total hidden nodes for each genotype in the population
	for ind in pop:
		allHiddenVals.append(ind.getHiddenNodes())
	# store all data for the frequency of hidden nodes in a dictionary
	dataDict = {}
	for val in allHiddenVals:
		if(val in dataDict.keys()):
			dataDict[val] = dataDict[val] + 1
		else:
			dataDict[val] = 1
	# create bar graph to display with given data
	ax = plt.subplot(111)
	ax.bar(dataDict.keys(), dataDict.values() ,width=0.2,color='b',align='center')
	plt.title("NUMBER OF HIDDEN NODES AMONG INDIVIDUALS")
	plt.xlabel("Number of Hidden Nodes")
	plt.ylabel("Frequency")
	# display the graph
	plt.show()

'''
creates bar graphing showing the number of connections in a the population's networks
shows frequency of each number of connections
@param pop population for which visualization is being generated
'''
def visConnections(pop):
	allConnections = []
	# generate all total number connection values for population
	for ind in pop:
		allConnections.append(len(ind.connections))
	# store all data in dictionary so that it can be turned into a bar graph
	dataDict = {}
	for val in allConnections:
		if(val in dataDict.keys()):
			dataDict[val] = dataDict[val] + 1
		else:
			dataDict[val] = 1
	# create bar graph to display with connection data
	ax = plt.subplot(111)
	ax.bar(dataDict.keys(), dataDict.values() ,width=0.2,color='b',align='center')
	plt.title("NUMBER OF CONNECTIONS AMONG INDIVIDUALS")
	plt.xlabel("Number of Connections")
	plt.ylabel("Frequency")
	# display the graph
	plt.show()


'''
The following function is used to visualize a general set of data
generates a bar graph containing all values and the frequencies 
associated with them 
@param dataSet the data set for which the bar graph is being generated
post: graph is displayed to user
'''
def visGeneralData(dataSet):
	dataDict = {}
	# generate dictionary based on given data
	for d in dataSet:
		if(d in dataDict.keys()):
			dataDict[d] = dataDict[d] + 1
		else:
			dataDict[d] = 1
	# plot data and show to user
	ax = plt.subplot(111)
	ax.bar(dataDict.keys(), dataDict.values() ,width=0.2,color='g',align='center')
	plt.title("VISUALIZATIN OF DATA SET")
	plt.xlabel("Value")
	plt.ylabel("Frequency")
	plt.show()


'''
method for quickly finding the number of solutions that passed XOR
@param pop the population of solutions that are being tested on XOR
@return tuple containing (number that passed test, number that failed test)
'''
def findNumGoodSolutions(pop):
	inputs = [[0,0],[0,1],[1,0],[1,1]]
	numSolved = 0
	numFailed = 0
	# evaluate XOR for every individual in population
	for ind in pop:
		outputs = []
		for ins in inputs:
			outputs.append(ind.getOutput(ins)[0])
		GOOD_THRESH = .4
		if(outputs[0] < GOOD_THRESH and outputs[1] > GOOD_THRESH and outputs[2] > GOOD_THRESH and outputs[3] < GOOD_THRESH):
			numSolved += 1
		else:
			numFailed +=1 

	return (numSolved, numFailed)
