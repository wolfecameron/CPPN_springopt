'''
* This file contains the node class used for the full CPPN implementation
* Node is one of the two structural components of the CPPN 
'''

import copy

from FULL_CPPN_act import stepAct, sigAct, reluAct, sinAct, gaussAct, logAct, tanhAct, squareAct, absAct

# Node class, defined in this file to be used in CPPN implementation
class Node: 	

	'''
	** constructor for node class
	@param nodeNumber the current number given to node being initialized
	@param value stored within the node when it is activated, usually 0 or changed when CPPN is activated
	@param layer topological value used to sort connection list before activating CPPN
	@param actKey used to decide which activation function to use when activating CPPN
	pre: 0 < actKey <= 5
	'''
	def __init__(self, nodeNumber, value, layer, actKey):
		if(actKey < 0 or actKey > 8):
			print("Error: actKey is not within range.")
		else:
			self.nodeNum = nodeNumber
			self.value = value
			# layer is not a true layer - only used for sorting nodes based on network topology
			self.layer = layer
			self.actKey = actKey


	'''
	The following methods are used as accessor methods for node class
	These methods should be used in place of direct access to instance variables
	'''
	def getNodeNum(self):
		return self.nodeNum

	def getNodeValue(self):
		return self.value

	def getNodeLayer(self):
		return self.layer

	def getActKey(self):
		return self.actKey

	'''
	The following methods are used as mutator methods for node class
	These methods should be used in place of directly changing instance variables
	@param newVal the new value to which the given instance variable is being changed
	'''
	def setNodeNum(self, newVal):
		self.nodeNum = newVal

	def setNodeValue(self, newVal):
		self.value = newVal

	def setNodeLayer(self, newVal):
		self.layer = newVal

	def setActKey(self, newVal):
		self.actKey = newVal

	'''
	the following method overrides the default equals method
	compares two nodes based on instance variables
	only take number into account, the rest of instance variables are arbitrary for equality
	@param other object to which calling object is being compared
	'''
	def __eq__(self, other):
		if isinstance(self,type(other)):
			return self.getNodeNum() == other.getNodeNum()
		return False


	'''
	toString method for node, prints string representation of a given node
	@return string representation of node
	'''
	def __str__(self):
		result = "\n"
		result += "***** NODE INFORMATION ***** \n"
		result += "Node Number: " 
		result += str(self.nodeNum) + "\n"
		result += "Node Value: " 
		result += str(self.value) + "\n"
		result += "Node Layer: " 
		result += str(self.layer) + "\n"
		result += "Activation: " 
		result += str(self.actKey) + "\n"
		result += "\n"
		return result
	'''
	method to get a deep copy of a given node
	@return a deep copy of the given node
	'''
	def getCopy(self):
		return copy.deepcopy(self)

	'''
	activates a node based on current value and activation key
	applies appropriate activation function and returns val
	@return output of activation function with current node value as its input
	'''
	def activate(self):
		val = self.getNodeValue()
		if(self.getActKey() == 0):
			val = stepAct(val)
		elif(self.getActKey() == 1):
			val = sigAct(val)
		elif(self.getActKey() == 2):
			val = reluAct(val)
		elif(self.getActKey() == 3):
			val = sinAct(val)
		elif(self.getActKey() == 4):
			val = gaussAct(val)
		elif(self.getActKey() == 5):
			val = logAct(val)
		elif(self.getActKey() == 6):
			val = tanhAct(val)
		elif(self.getActKey() == 7):
			val = squareAct(val)
		elif(self.getActKey() == 8):
			val = absAct(val)
		return val
