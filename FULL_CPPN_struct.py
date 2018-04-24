from FULL_CPPN_node import Node
from FULL_CPPN_con import Connection
import sys
import random as r
import numpy as np

'''
This class implements the actual structure of the CPPN, or the genotype
All mutation, crossover, and activation features are implemented in the structure
'''

# genotype class implements the CPPN structure
class Genotype():

	'''
	Constructor for the genotype class, initializes genotype object and builds initial, simple network
	@param numIn the number of inputs into the network (excluding bias)
	@param numOut the number of outputs out of the network
	'''
	def __init__(self, numIn, numOut):

		# add one to numIn to account for bias
		self.numIn = numIn + 1 
		self.numOut = numOut
		self.gSize = self.numIn + self.numOut
		self.nodes = []
		self.connections = []
		self.fitness = 0
		# variable used to keep nodes in topological order
		self.highestTopology = 0

		# create input nodes
		for i in range(self.numIn):
			self.nodes.append(Node(i,0,0,1))

		# create output nodes
		for i in range(self.numOut):
			self.nodes.append(Node(i + self.numIn,0,sys.maxsize,1))

		# used to track innovation number as connections are created
		innovationCounter = 0
		
		# fully connect all inputs to outputs, must handle innovation numbers
		for x in range(self.numIn):
			for y in range(self.numOut):
				initWeight = r.uniform(-2,2)
				self.connections.append(Connection(self.nodes[x], self.nodes[self.numIn + y], initWeight, innovationCounter))
				innovationCounter += 1
	
	# accessor methods for genotype
	def size(self):
		return self.gSize

	def getNodes(self):
		return self.nodes

	def getConnections(self):
		return self.connections

	# basic mutator methods were not needed for this class, node and connection lists modified by mutation/XOVER methods etc
	''' 
	node mutation method for CPPN
	picks an active connection in the network and splits it in half, inserting a node in middle
	adds two connections from the initial node to the newNdode and from the newNode to the terminal node
	nothing is returned by this mutation method
	@param innovation1/2 new innovation numbers for the first and second new connection
	NOTE: EVENTUALLY WANT TO PASS IN A MAP OF CONNECTIONS TO INNOVATION NUMBERS TO CHECK
	'''
	def nodeMutate(self, innovation1, innovation2):
		# pick a random location in the connections, find connection to split
		conInd = r.randint(0,len(self.connections))	
		ogIndex = conInd - 1 # use to prevent infinite loop in case all connections deactivated
		while((not self.connections[conInd % len(self.connections)].getStatus()) and not(conInd == ogIndex)):
			conInd += 1
		# deactivate old connection and insert new node 
		connect = self.connections[conInd]
		connect.setStatus(False)
		oldOut = connect.getNodeOut()
		oldIn = connect.getNodeIn()
		newLayer = oldIn.getNodeLayer() + ((oldOut.getNodeLayer() - oldIn.getNodeLayer()) / 2) # new layer in between others
		self.nodes.append(Node(size() + 1, 0, newLayer, 1))
		self.gSize += 1
		# add connections for new node, first one has original weight and second has weight of 1
		self.connections.append(Connection(oldIn, self.nodes[size() - 1], connect.getWeight(), innovation1))
		self.connections.append(Connection(self.nodes[size() - 1], oldOut, 1, innovation2))
		# Note, the validity of these connections is ensured because of the way the original connection is split


	''' 
	weight mutation method for CPPN
	alters a weight from a random connection in the CPPN
	@param mutpb float value between 0-1 that specifies the probability of weight mutation
	@return true if any weight mutation was applied false otherwise
	'''
	def weightMutate(self, mutpb):
		mutate = False
		variance = 1.0
		for c in self.connections:
			if(r.random() <= mutpb):
				# mutate weights based on a normal distribution around old weight
				mutate = True
				c.weight = np.random.normal(c.weight, variance)
		return mutate

	'''
	activation mutatation function for CPPN structure
	goes through entire node list and changes activation keys for functions
	@param mutpb probability of a node's actKey being mutated 
	@return true if any node was mutated false otherwise
	'''
	def activationMutate(self, mutpb):
		mutate = False
		for n in self.nodes:
			if(r.random() <= mutpb):
				# mutate act by selecting a random actKey
				mutate = True
				n.setActKey(random.choice([1]))
		return mutate

	'''
	connection mutate method for the CPPN structure
	adds a new connection into the current CPPN topology
	@param innovation innovation number to assign to the new connection
	@return true if connection was added to topology false otherwise
	'''
	def connectionMutate(self, innovation):
		# sort nodes based on topology of CPPN
		sortedNodes = sorted(self.nodes,key = lambda x: x.getNodeLayer())
		foundGoodConnection = False
		tryCount = 0
		maxTries = 50
		newWeight = r.uniform(-2,2)
		# only allow network to attempt to form connections a certain number of times - prevents infinite loop
		while(not foundGoodConnection and tryCount < maxTries):
			# choose two random indexes for in and out nodes of connection such that in < out
			inInd = r.randint(0,len(sortedNodes) - 2)
			outInd = r.randInt(inInd, len(sortedNodes) - 1)
			# create possible connection and check if valid
			connect = Connection(self.nodes[inInd],self.nodes[outInd],newWeight,innovation)
			if(validConnection(connect)):
				foundGoodConnection = True
			tryCount += 1
		return foundGoodConnection
	
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
		if(otherCon.getNodeIn().getNodeLayer() >= otherCon.getNodeIn().getNodeLayer()):
			valid = False
		return valid







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
		result += "----- NODES (number,type,actKey) ------\n"
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
			result += "(" + str(n.getNodeNum()) + "," + nType + str(n.getActKey()) + ")\n"
		result += "\n"
		result += "----- CONNECTIONS -----\n"
		result += "\n"
		for c in self.connections:
			result += str(c.getNodeIn().getNodeNum()) + " >>> " + str(c.getWeight()) + " >>> " + str(c.getNodeOut().getNodeNum())
			result += "\n"
		result += "\n"
		return result
