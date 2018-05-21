'''
This file declared the GlobalInnovation class 
this class stores a single integer value and a dictionary 
which are each used to track the creation of innovation numbers
throughout the evolution process
'''

class GlobalInnovation():

	'''
	constructor for the GlobalInnovation class
	initializes the integer value of GlobalInnovation and
	the dictionary used to store topology mutations
	'''
	def __init__(self, numIn, numOut):
		numInitialCons = (numIn + 1)*numOut
		# current stores the next innovation number to be assigned to 
		# a novel mutation
		self.current = numInitialCons
		# innov dict stores entries representing all new connections that have 
		# been created in a given generation
		self.innovDict = {}

	'''
	method to retrieve next available innovation number
	@return next available innovation number
	'''
	def getNextInnov(self):
		curr = self.current 
		return curr

	'''
	method for incrementing the current global innovation number
	@return nothing
	post: globalInnovation number is incremented
	'''
	def incrementInnov(self):
		self.current += 1


	'''
	method to add an entry into the current innovation dictionary
	@oldInnov integer value representing the innovation number of the connection
	that was split in the genotype
	@newInnovs tuple of values representing the connection going IN TO the new node
	and OUT OF the new node in form (IN, OUT)
	@return nothing
	post: new entry is added into the dictionary
	'''
	def addToDict(oldInnov, newInnovs):
		self.innovDict[oldInnov] = newInnovs


	'''
	method for clearing the innovation dictionary
	this should be done at the end of every generation
	mutations only tracked to be the same during a single generation
	post: dictionary is empty
	'''
	def clearDict(self):
		self.innovDict = {}


	'''
	toString function for the GlobalInnovation class
	prints out all current data stored in the class
	'''
	def __str__(self):
		result = ""
		result += ("NEXT INNOVATION NUMBER: " + str(self.current) + "\n")
		result += ("CURRENT DICTIONARY STATE: " + str(self.innovDict) + "\n")
		return result