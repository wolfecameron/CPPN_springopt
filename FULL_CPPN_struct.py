from FULL_CPPN_node import Node
from FULL_CPPN_con import Connection
import sys
import random as r

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
