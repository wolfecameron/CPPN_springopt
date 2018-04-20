'''
This file contains the implementation of the Connection class for CPPN
The connection object is the other major portion of the CPPN genotype
in addition to the node
'''

class Connection():

	'''
	Constructor for the connection class
	@param nodeIn the initial vertex of the connection
	@param nodeOut the terminal vertex of the connection
	@param weight weight of the connection (what value is multiplied by during activation)
	@param innovation innovation number for this gene
	NOTE: innovation number should be determined by a global counter in the main evolution process
	'''

	def __init__(self,nodeIn, nodeOut, weight, innovation):

		self.nIn = nodeIn
		self.nOut = nodeOut
		self.weight = weight
		self.status = True # boolean variable for activation status of connection
		self.innovationNumber = innovation

	'''
	The following methods are all accessor methods for connection class
	These methods should be used in place of directly referencing instance variables
	'''
	def getNodeIn(self):
		return self.nIn

	def getNodeOut(self):
		return self.nOut

	def getWeight():
		return self.weight

	def getStatus():
		return self.status

	def getInnovationNumber():
		return self.innovationNumber

	'''
	The following methods are all mutator methods for connection class
	These methods should be used in place of directly changing instance variables
	setter method for innovation number not given because this should never be changed
	'''
	def setNodeIn(self, nodeIn):
		self.nIn = nodeIn

	def setNodeOut(self, nodeOut):
		self.nOut = nodeOut

	def setWeight(self, w):
		self.weight = w

	def setStatus(self, status):
		self.status = status

	'''
	Overrides generic equals method 
	Two connections considered equal if nodeIn, nodeOut, and status are the same
	Status included because if connection is deactivated it could be added again into network
	'''
	def __eq__(self, other):
    	if isinstance(self, other.__class__):
    		# allow of below conditions must be true to be equal connection
        	result = self.getNodeIn() == other.getNodeIn() 
        	result = result and self.getNodeOut() == other.getNodeOut() 
        	result = result and self.getStatus() == other.getStatus
        	return result
    return False
