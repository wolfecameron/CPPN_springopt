'''
* This file contains the node class used for the full CPPN implementation
* Node is one of the two structural components of the CPPN 
'''

# Node class, defined in this file to be used in CPPN implementation
class Node(): 	

	'''
	** constructor for node class
	@param nodeNumber the current number given to node being initialized
	@param value stored within the node when it is activated, usually 0 or changed when CPPN is activated
	@param layer topological value used to sort connection list before activating CPPN
	@param actKey used to decide which activation function to use when activating CPPN
	'''
	def __init__(self, nodeNumber, value, layer, actKey):

		self.nodeNum = nodeNumber
		self.value = value
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
	toString method for node, prints string representation of a given node
	@return string representation of node
	'''
	def __str__(self):
		result = ""
		result += "***** NODE INFORMATION ***** \n"
		result += "Node Number: " 
		result += str(self.nodeNum) + "\n"
		result += "Node Value: " 
		result += str(self.value) + "\n"
		result += "Node Layer: " 
		result += str(self.layer) + "\n"
		result += "Activation: " 
		result += str(self.actKey) + "\n"
		return result
