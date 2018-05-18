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