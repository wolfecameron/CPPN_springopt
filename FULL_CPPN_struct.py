'''
This class implements the actual structure of the CPPN, or the genotype
All mutation, crossover, and activation features are implemented in the structure
'''

import sys
import copy

import random as r
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from FULL_CPPN_node import Node
from FULL_CPPN_con import Connection


# genotype class implements the CPPN structure
class Genotype():

	# all default values for constructor parameters declared below
	DEF_NUMIN = 2
	DEF_NUMOUT = 1

	'''
	Constructor for the genotype class, initializes genotype object and builds initial, simple network
	@param numIn the number of inputs into the network (excluding bias)
	@param numOut the number of outputs out of the network
	'''
	def __init__(self, numIn = DEF_NUMIN, numOut = DEF_NUMOUT):
		# add one to numIn to account for bias
		self.numIn = numIn + 1 
		self.numOut = numOut
		self.gSize = self.numIn + self.numOut
		self.nodes = []
		self.connections = []
		self.fitness = 0

		# sepcies instance variable used to track species in a population
		# assigned in the speciation method based on distance to other members of a species 
		self.species = sys.maxsize

		# create input nodes
		for i in range(self.numIn):
			self.nodes.append(Node(i,0,0,r.choice([0,1,2,3,4,5,6,7,8])))

		# create output nodes, output nodes always have step function
		for i in range(self.numOut):
			self.nodes.append(Node(i + self.numIn,0,sys.maxsize,1))#0))

		# used to track innovation number as connections are created
		innovationCounter = 0

		# initialize weights between -1/(numConnections) -> 1/(numConnections)
		weightRange = 1/float(self.numIn)
		
		# fully connect all inputs to outputs, must handle innovation numbers
		for x in range(self.numIn):
			for y in range(self.numOut):
				initWeight = np.random.normal(0, weightRange)
				self.connections.append(Connection(self.nodes[x], self.nodes[self.numIn + y], initWeight, innovationCounter))
				innovationCounter += 1
	
	# accessor methods for genotype
	def size(self):
		return self.gSize

	def getNodes(self):
		return self.nodes

	def getConnections(self):
		return self.connections

	def getFitness(self):
		return self.fitness

	# basic mutator methods for genotype
	def setFitness(self, newFit):
		self.fitness = newFit


	'''
	method to run the CPPN and get output of the network
	@param inputs inputs into the network
	@return output of the network with given inputs
	pre: len(inputs) == self.numIn - 1
	'''
	def getOutput(self, inputs):
		if(not(len(inputs) == (self.numIn - 1))):
			print("The length of the list of inputs does not match the number of desired inputs.")
		else:
			# must clear all node values before running the network
			self.clearAllValues()
			
			# sort connections list by the layer of the in node
			sortedConnection = sorted(self.connections, key = lambda x: x.getNodeIn().getNodeLayer())
			
			# set values of input nodes
			for nodeInd in range(self.numIn - 1):
				self.nodes[nodeInd].setNodeValue(inputs[nodeInd])
			
			# set value of bias node
			self.nodes[self.numIn - 1].setNodeValue(1)
			
			# activate network by going through sorted connection list and querying all connections
			for c in range(len(sortedConnection)):
				if(sortedConnection[c].getStatus()):
					# do not activate the inputs, only hidden/output nodes
					if sortedConnection[c].getNodeIn().getNodeLayer() > 0:		
						# FORMULA: nodeOut.val += activation(nodeIn.val)*weight
						sortedConnection[c].getNodeOut().setNodeValue(sortedConnection[c].getNodeOut().getNodeValue() + (sortedConnection[c].getNodeIn().activate()*sortedConnection[c].getWeight()))
					else:
						sortedConnection[c].getNodeOut().setNodeValue(sortedConnection[c].getNodeOut().getNodeValue() + (sortedConnection[c].getNodeIn().getNodeValue()*sortedConnection[c].getWeight()))
			
			# put all output values in a single list and return
			outputs = [] 
			outInd = self.numIn 
			foundAllOutputs = False
			while(outInd < len(self.nodes) and not foundAllOutputs):
				if(self.nodes[outInd].getNodeLayer() == sys.maxsize):
					out = self.nodes[outInd].activate()
					outputs.append(out)
				else:
					foundAllOutputs = True
				outInd += 1
			
			return outputs

	'''
	helper method for getOutput
	clears all node values to 0 before activating the network
	'''
	def clearAllValues(self):
		for nodeInd in range(len(self.nodes)):
			self.nodes[nodeInd].setNodeValue(0)


	# basic mutator methods were not needed for this class, node and connection lists modified by mutation/XOVER methods etc
	''' 
	node mutation method for CPPN
	picks an active connection in the network and splits it in half, inserting a node in middle
	adds two connections from the initial node to the newNdode and from the newNode to the terminal node
	nothing is returned by this mutation method
	@param innovation1/2 new innovation numbers for the first and second new connection
	@param innovationMap dictionary containing key-value of (inNode,outNode) -> innovation number
	@param globalInnovation current value of the global innovation counter being used
	@return new state of innovationMap and innovationCounter after new node/connections added
	'''
	def nodeMutate(self, innovationMap, globalInnovation):
		# pick a random location in the connections, find connection to split
		conInd = r.randint(0,len(self.connections) - 1)	
		ogIndex = conInd - 1 # use to prevent infinite loop in case all connections deactivated
		while((not self.connections[conInd % len(self.connections)].getStatus()) and not(conInd == ogIndex)):
			conInd += 1

		# deactivate old connection and insert new node 
		connect = self.connections[conInd % len(self.connections)]
		connect.setStatus(False)
		oldInnov = connect.getInnovationNumber()
		oldOut = connect.getNodeOut()
		oldIn = connect.getNodeIn()

		# layer of new node halfway between two parent nodes
		newLayer = oldIn.getNodeLayer() + ((oldOut.getNodeLayer() - oldIn.getNodeLayer()) / 2)
		self.nodes.append(Node(self.size(), 0, newLayer, r.choice([0,1,2,3,4,5,6,7,8])))
		self.gSize += 1

		# check current innovationMap to determine innovation numbers of two new connections
		innovation1 = 0
		innovation2 = 0
		k = innovationMap.keys()

		# check innovation map to see if this structural mutation has occurred in this generation already
		# map format: (innovation # of gene that is split) --> (new in connection innov num, new out connection innov num)
		if(oldInnov in k):
			innov = innovationMap[oldInnov]
			innovation1 = innov[0]
			innovation2 = innov[1]
		else:
			# add this mutation into the map for this generation just in case it occurs again
			innovation1 = globalInnovation
			innovation2 = globalInnovation + 1
			globalInnovation += 2
			innovationMap[oldInnov] = (innovation1, innovation2)

		# add connections for new node, first one has original weight and second has weight of 1
		self.connections.append(Connection(oldIn, self.nodes[self.size() - 1], 1, innovation1))
		self.connections.append(Connection(self.nodes[self.size() - 1], oldOut, connect.getWeight(), innovation2))

		#species number already set to default when fittest individuals retrieved from species
		return (innovationMap, globalInnovation)

	'''
	method to find number of hidden nodes in a given structure
	@return number of hidden nodes in calling genotype
	'''
	def getHiddenNodes(self):
		# num hidden can be determined using instance variables
		return self.size() - self.numIn - self.numOut

	''' 
	weight mutation method for CPPN
	alters a weight from a random connection in the CPPN
	@param mutpb float value between 0-1 that specifies the probability of weight mutation
	@return true if any weight mutation was applied false otherwise
	'''
	def weightMutate(self):
		variance = 1.0
		typeOfChange_pb = .9
		for c in self.connections:
			# 90% chance to perturb weight, 10% chance to pick completely new one
			if(r.random() <= typeOfChange_pb):
				# mutate weights based on a normal distribution around old weight
				c.setWeight(np.random.normal(c.weight, variance))
			else:
				# set weight equal to something new
				c.setWeight(r.uniform(-1,1))

	'''
	activation mutatation function for CPPN structure
	takes random node in node list and changes its activation function
	@return true if any node was mutated false otherwise
	'''
	def activationMutate(self):
		foundPossible = False
		index = r.randint(0,len(self.nodes) - 1)
		foundPossible = False
		while(not foundPossible):
			# act function of output nodes should never be changed
			if(not self.nodes[index].getNodeLayer() == sys.maxsize):
				foundPossible = True
			else:
				index = r.randint(0,len(self.nodes) - 1)
		self.nodes[index].setActKey(r.choice([0,1,2,3,4,5,6,7,8]))

	'''
	connection mutate method for the CPPN structure
	adds a new connection into the current CPPN topology
	@param innovationMap dictionary containing key-value of (inNode,outNode) -> innovation number
	@param globalInnovation current global count of innovation numbers
	@return updated state of innovationMap and globalInnovation
	'''
	def connectionMutate(self, globalInnovation):
		# sort nodes based on topology of CPPN
		foundGoodConnection = False
		tryCount = 0
		maxTries = 20
		newWeight = r.uniform(-0.5,0.5)
		connect = None
		# only allow network to attempt to form connections a certain number of times - prevents infinite loop
		while(not foundGoodConnection and tryCount < maxTries):
			# choose two random indexes for in and out nodes of connection such that in < out
			inInd = r.randint(0,len(self.nodes) - 1) 
			outInd = r.randint(0, len(self.nodes) - 1)
			# create possible connection and check if valid
			connect = Connection(self.nodes[inInd], self.nodes[outInd], newWeight, globalInnovation)
			# if a valid connection is found, add it into the network and increment the global innovation count
			if(self.validConnection(connect)):
				foundGoodConnection = True
				self.connections.append(connect)
				globalInnovation += 1
			tryCount += 1
		
		return globalInnovation
	

	'''
	method to check is a given connection is valid
	connection considered valid if it nodeIn has a layer less than nodeOut
	and if the connection is not already present in connection list
	@param otherCon the connection that is being checked for validity
	@return true if connection is valid and false otherwise
	'''
	def validConnection(self, otherCon):
		valid = True
		for c in self.connections:
			if c == otherCon:
				valid = False
		# check that connection is going upwards in layer
		if(otherCon.getNodeIn().getNodeLayer() >= otherCon.getNodeOut().getNodeLayer()):
			valid = False
		return valid

	'''
	crossover function for two Genotypes 
	takes all genes from fitter parent and adds to new individual
	then takes genes that are same between two parents and chooses randomly between them
	@param other the Genotype that is being crossed over with the calling genotype
	@param pointcxpb probability that genes with similar innov num will be swapped for each iteration
	@return a new individual that is the retult of crossover
	MAKE 3 DIFFERENT CROSSOVERS - gaussian and average!!!!
	'''
	def crossover(self, other):
		# keep disjoint genes from more fit parent
		child = None
		parent = None
		if(self.getFitness() > other.getFitness()):
			child = self.getCopy()
			parent = other.getCopy()
		else:
			child = other.getCopy()
			parent = self.getCopy()
		# traverse connection, crossover those with same innov number
		for childInd in range(len(child.connections)):
			for parInd in range(len(parent.connections)):
				if(child.connections[childInd].getInnovationNumber() == parent.connections[parInd].getInnovationNumber()):
					# swap genes if random number below pointcxpb
					swap = r.random()
					if(swap <= .25):
						# TAKE WEIGHT HERE NOT THE CONNECTION
						child.connections[childInd] = parent.connections[parInd].getCopy()
		
		return child

	'''
	crossover function for two Genotypes
	Same as other crossover but this one creates two new individuals to return 
	takes all genes from fitter parent and adds to new individual
	then takes genes that are same between two parents and chooses randomly between them
	@param other the Genotype that is being crossed over with the calling genotype
	@param pointcxpb probability that genes with similar innov num will be swapped for each iteration
	@return a tuple containing the two newly crossed over individuals
	MAKE 3 DIFFERENT CROSSOVERS - gaussian and average!!!!
	'''
	def crossoverReturnBoth(self, other):
		# keep disjoint genes from more fit parent
		SWAP_PB = .25
		child = None
		parent = None
		if(self.getFitness() > other.getFitness()):
			child = self.getCopy()
			parent = other.getCopy()
		else:
			child = other.getCopy()
			parent = self.getCopy()
		betterInd = child.getCopy() # return crossover over individual and the original fitter individual
		# traverse connection, crossover those with same innov number
		for childInd in range(len(child.connections)):
			for parInd in range(len(parent.connections)):
				if(child.connections[childInd].getInnovationNumber() == parent.connections[parInd].getInnovationNumber()):
					# swap genes if random number below pointcxpb
					swap = r.random()
					if(swap <= SWAP_PB):
						# swap the connections between the two individuals
						tmp = child.connections[childInd].getWeight()
						child.connections[childInd].setWeight(parent.connections[parInd].getWeight())
						parent.connections[parInd].setWeight(tmp)
		
		return (child, betterInd)


	'''
	Another type of crossover functions
	same as the one above, exept instead of switching the weights,
	the average of the weights is found and this is what's used for the child's weight
	@param other the other individuals with which this genome is being crossed over
	@return individual that has been crossed over with other and the better individual of the two
	(child, betterInd)
	'''
	def crossoverAvg(self, other):
		# find more fit parent and this will serve as beginning for new child
		SWAP_PB = .5
		child = None
		parent = None
		if(self.getFitness() > other.getFitness()):
			child = self.getCopy()
			parent = other.getCopy()
		else:
			child = other.getCopy()
			parent = self.getCopy()
		betterInd = child.getCopy() # return crossover over individual and the original fitter individual
		# traverse connection, crossover those with same innov number
		for childInd in range(len(child.connections)):
			for parInd in range(len(parent.connections)):
				if(child.connections[childInd].getInnovationNumber() == parent.connections[parInd].getInnovationNumber()):
					# swap genes if random number below pointcxpb
					swap = r.random()
					if(swap <= SWAP_PB):
						# find the average of two weights and set this equal to weight for the child
						newWeight = (child.connections[childInd].getWeight() + parent.connections[parInd].getWeight())/2
						child.connections[childInd].setWeight(newWeight)
		
		return (child, betterInd)


	'''
	method to find the distance between two networks' topologies
	used for speciation of different network topologies
	@param other the other structure for which distance is being found
	@param theta1,2,3 weights given to disjoint genes, excess genes, and average weight difference
	@return integer value representing distance between two network structures
	'''
	def getDistance(self, other, theta1, theta2, theta3):
		# find max and min innov number to determine if nodes excess or disjoint
		innovRange = other.findRangeOfInnovationNumbers()
		minInnov = innovRange[0]
		maxInnov = innovRange[1]
		numDisjoint = 0.0
		numExcess = 0.0
		for con in self.connections:
			currInnov = con.getInnovationNumber()
			if(currInnov < minInnov or currInnov > maxInnov):
				numExcess += 1
			oInd = 0
			found = False
			while(oInd < len(other.connections) and not found):
				if(other.connections[oInd].getInnovationNumber() == currInnov):
					found = True
				oInd += 1
			if(not found):
				numDisjoint += 1
		# must calculate average weight difference between matching genes
		weightDifference = 0.0
		numMatchingConnections = 0
		for con1 in self.connections:
			for con2 in other.connections:
				if(con1.getInnovationNumber() == con2.getInnovationNumber()):
					weightDifference += np.fabs(con1.getWeight() - con2.getWeight())
					numMatchingConnections += 1
		weightDifference /= numMatchingConnections
		# N is the number of genes in the larger genome
		N = len(self.connections) if (len(self.connections) > len(other.connections)) else len(other.connections)
		
		# distance formula: O1*disjoint + O2*excess + O3*averageWeightDiff
		return ((theta1*numExcess)/N) + ((theta2*numDisjoint)/N) + ((theta3*weightDifference))


	'''
	helper method for get distance method
	returns the total sum of weight across all connections in a network
	@return average value of weights for calling network
	'''
	def getTotalWeight(self):
		weightTotal = 0.0
		for c in self.connections:
			weightTotal += c.getWeight()
		return weightTotal

	'''
	method for getting the average distance between calling genome and a list of others
	@param others list of other genotypes
	@param theta1-3 described above
	@return average distance from calling genotype to all individuals in given list
	'''
	def getAverageDistance(self, others, theta1, theta2, theta3):
		totalDistance = 0.0
		# add all distances to the total distance
		for other in others:
			totalDistance += self.getDistance(other, theta1, theta2, theta3)
		
		return totalDistance/len(others)

	'''
	helper method for getDistance method
	finds the range of innovation numbers in the calling object
	@return a tuple containing (min innov #, max innov #)
	'''
	def findRangeOfInnovationNumbers(self):
		# set max in min initially to worst values possible
		maxInnov = -1
		minInnov = sys.maxsize
		for c in self.connections:
			if(c.getInnovationNumber() > maxInnov):
				maxInnov = c.getInnovationNumber()
			if(c.getInnovationNumber() < minInnov):
				minInnov = c.getInnovationNumber()
		
		return (minInnov, maxInnov)


	def graph_genotype(self):
		"""Creates a graph of the network's genotypes using the
		python networkx module
		"""

		graph = nx.Graph()

		# add each node into the graph - node number used to map the nodes
		# in CPPN to the corresponding nodes in the graph
		for node in self.nodes:
			graph.add_node(node.getNodeNum())

		# create all connections in graph
		for con in self.connections:
			graph.add_edge(con.getNodeIn().getNodeNum(), 
							con.getNodeOut().getNodeNum())

		# display graph to user
		plt.subplot(111)
		nx.draw(graph, with_labels=True, font_weight='bold')
		plt.show()


	'''
	toString method for Genotype class
	@return string representation of a given genotype
	'''
	def __str__(self):
		result = "\n"
		result += "***** GENOTYPE INFORMATION *****\n"
		result += "\n"
		result += "INPUT NODES: " + str(self.numIn -1) + "\n"
		result += "OUTPUT NODES: " + str(self.numOut) + "\n"
		result += "TOTAL SIZE: " + str(self.size()) + "\n"
		result += "\n"
		result += "----- NODES (number,type,actKey,layer) ------\n"
		result += "\n"
		for n in self.nodes:
			lay = n.getNodeLayer()
			nType = ""
			if(lay == 0):
				nType = "input,"
			elif(lay == sys.maxsize):
				nType = "output,"
			else:
				nType = "hidden,"
			result += "(" + str(n.getNodeNum()) + "," + nType + str(n.getActKey()) + "," + str(n.getNodeLayer()) + ")\n"
		result += "\n"
		result += "----- CONNECTIONS -----\n"
		result += "\n"
		for c in self.connections:
			if c.getStatus():
				result += str(c.getNodeIn().getNodeNum()) + " >>> " + str(c.getWeight()) + " >>> " + str(c.getNodeOut().getNodeNum()) + " [" + str(c.getInnovationNumber()) + "]"
				result += "\n"
		result += "\n"
		return result

	'''
	method to create a deep copy of calling genotype
	@return a deep copy of the calling genotype
	'''
	def getCopy(self):
		return copy.deepcopy(self)

if __name__ == "__main__":
	"""Main function used for quick testing"""
	g = Genotype(2, 1)
	g.graph_genotype()