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
			self.nodes.append(Node(i,0,0,r.choice([0,1,2,3,4,5])))

		# create output nodes, output nodes always have step function
		for i in range(self.numOut):
			self.nodes.append(Node(i + self.numIn,0,sys.maxsize,0))

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
			# sort connections list by the layer of the in node
			sortedConnection = sorted(self.connections,key = lambda x: x.getNodeIn().getNodeLayer())
			# set values of input nodes
			for nodeInd in range(self.numIn - 1):
				self.nodes[nodeInd].setNodeValue(inputs[nodeInd])
			# set value of bias node
			self.nodes[self.numIn - 1].setNodeValue(1)
			# activate network by going through connection list and querying all connections
			for c in self.connections:
				# FORMULA: nodeOut.val += activation(nodeIn.val)*weight
				c.getNodeOut().setNodeValue(c.getNodeOut().getNodeValue() + (c.getNodeIn().activate()*c.getWeight()))
			# put all output values in a single list and return
			outputs = [] 
			outInd = self.numIn 
			foundAllOutputs = False
			while(outInd < len(self.nodes) and not foundAllOutputs):
				if(self.nodes[outInd].getNodeLayer() == sys.maxsize):
					out = self.nodes[outInd].getNodeValue()
					outputs.append(out)
				else:
					foundAllOutputs = True
				outInd += 1
			return outputs




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
		conInd = r.randint(0,len(self.connections))	
		ogIndex = conInd - 1 # use to prevent infinite loop in case all connections deactivated
		while((not self.connections[conInd % len(self.connections)].getStatus()) and not(conInd == ogIndex)):
			conInd += 1
		# deactivate old connection and insert new node 
		connect = self.connections[conInd]
		connect.setStatus(False)
		oldOut = connect.getNodeOut()
		oldIn = connect.getNodeIn()
		# layer of new node halfway between two parent nodes
		newLayer = oldIn.getNodeLayer() + ((oldOut.getNodeLayer() - oldIn.getNodeLayer()) / 2)
		self.nodes.append(Node(size() + 1, 0, newLayer, r.choice([0,1,2,3,4,5])))
		self.gSize += 1
		# check current innovationMap to determine innovation numbers of two new connections
		con1 = (oldIn.getNodeNum(),self.nodes[size() - 1].getNodeNum())
		con2 = (self.nodes[size() - 1].getNodeNum(), oldOut.getNodeNum())
		innovation1 = 0
		innovation2 = 0
		k = innovationMap.keys()
		# if either of these connections exist, assign to them correct innovation number
		# otherwise given them next available innovation number
		if(con1 in k):
			innovation1 = innovationMap[con1]
		else:
			innovation1 = globalInnovation
			innovationMap[con1] = innovation1
			globalInnovation += 1
		if(con2 in k):
			innovation2 = innovationMap[con2]
		else:
			innovation2 = globalInnovation
			innovationMap[con2] = innovation2
			globalInnovation += 1
		# add connections for new node, first one has original weight and second has weight of 1
		self.connections.append(Connection(oldIn, self.nodes[size() - 1], connect.getWeight(), innovation1))
		self.connections.append(Connection(self.nodes[size() - 1], oldOut, 1, innovation2))
		return (globalInnovation, innovationCounter)


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
	takes random node in node list and changes its activation function
	@return true if any node was mutated false otherwise
	'''
	def activationMutate(self):
		foundPossible = False
		index = r.randint(0,len(self.nodes) - 1)
		while(not foundPossible):
			if(not self.nodes[index].getNodeLayer() == sys.maxsize):
				foundPossible = True
			else:
				index = r.randint(0,len(self.nodes) - 1)
		self.nodes[index].setActKey(random.choice([0,1,2,3,4,5]))

	'''
	connection mutate method for the CPPN structure
	adds a new connection into the current CPPN topology
	@param innovationMap dictionary containing key-value of (inNode,outNode) -> innovation number
	@param globalInnovation current global count of innovation numbers
	@return updated state of innovationMap and globalInnovation
	'''
	def connectionMutate(self, innovationMap, globalInnovation):
		# sort nodes based on topology of CPPN
		sortedNodes = sorted(self.nodes,key = lambda x: x.getNodeLayer())
		foundGoodConnection = False
		tryCount = 0
		maxTries = 50
		newWeight = r.uniform(-2,2)
		connect = None
		# only allow network to attempt to form connections a certain number of times - prevents infinite loop
		while(not foundGoodConnection and tryCount < maxTries):
			# choose two random indexes for in and out nodes of connection such that in < out
			inInd = r.randint(0,len(sortedNodes) - 2) 
			outInd = r.randInt(inInd, len(sortedNodes) - 1)
			# create possible connection and check if valid
			connect = Connection(self.nodes[inInd],self.nodes[outInd],newWeight,0)
			if(validConnection(connect)):
				foundGoodConnection = True
			tryCount += 1
		if(foundGoodConnection):
			# check if new conneciton is already created and assign innovation accordingly 
			conTup = (connect.getNodeIn().getNodeNum(), connect.getNodeOut().getNodeNum())		
			if(conTup in innovationMap.keys()):
				innovation = innovationMap[conTup]
				self.connections.append(Connection(connect.getNodeIn(), connect.getNodeOut(), connect.getWeight(),innovation))
			else:
				self.connections.append(Connection(connect.getNodeIn(), connect.getNodeOut(), connect.getWeight(), globalInnovation))
				innovationMap[conTup] = globalInnovation
				globalInnovation += 1
		# return updated version of innovationMap and globalInnovation
		return (innovationMap, globalInnovation)
	

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
	crossover function for two Genotypes 
	takes all genes from fitter parent and adds to new individual
	then takes genes that are same between two parents and chooses randomly between them
	@param other the Genotype that is being crossed over with the calling genotype
	@param pointcxpb probability that genes with similar innov num will be swapped for each iteration
	@return a new individual that is the retult of crossover
	'''
	def crossover(self, other):
		# keep disjoint genes from more fit parent
		child = None
		parent = None
		if(self.getFitness() > other.getFitness):
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
					if(swap <= .5):
						child.connections[childInd] = parent.connections[parInd].getCopy()
		return child



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

	'''
	method to create a deep copy of calling genotype
	@return a deep copy of the calling genotype
	'''
	def getCopy(self):
		newGen = Genotype(self.numIn - 1, self.numOut)
		for n in self.nodes:
			newN = n.getCopy()
			newGen.nodes.append(newN)
		for c in self.connections:
			newC = c.getCopy()
			newGen.connections.append(newC)
		return newGen
