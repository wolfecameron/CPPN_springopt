"""This file contains all code used to parallelize the 
ea code for CPPN using scoop
"""

from scoop import futures
import numpy as np

from FULL_CPPN_act import stepAct, sigAct, reluAct, sinAct, gaussAct, logAct, tanhAct, squareAct, absAct


def activate_CPPN_scoop(input_tup):
	"""method for running an activation function on a CPPN
	must be reimplemented outside of the CPPN class so that
	it can be pickled by scoop

	Parameters:
	genotype -- the CPPN object being activated
	inputs -- the inputs into the CPPN
	"""
	genotype = input_tup[0]
	inputs = input_tup[1]
	if(not(len(inputs) == (genotype.numIn - 1))):
			print("The length of the list of inputs does not match the number of desired inputs.")
	else:
		if(not genotype.cons_sorted):
			genotype.connections = sorted(genotype.connections, key=lambda x: x.nIn.layer)
			genotype.cons_sorted = True
		# must clear all node values before running the network
		for node in genotype.nodes:
			node.value = 0

		# set values of input nodes
		for nodeInd in range(genotype.numIn - 1):
			genotype.nodes[nodeInd].value = inputs[nodeInd]
		
		# set value of bias node
		genotype.nodes[genotype.numIn - 1].value = 1
			
		# activate network by going through sorted connection list and querying all connections
		for c in range(len(genotype.connections)):
			if(genotype.connections[c].status):
				# do not activate the inputs, only hidden/output nodes
				if genotype.connections[c].nIn.layer > 0:		
					# FORMULA: nodeOut.val += activation(nodeIn.val)*weight
					genotype.connections[c].nOut.value = (genotype.connections[c].nOut.value + (activate_scoop(genotype.connections[c].nIn)*genotype.connections[c].weight))
				else:
					genotype.connections[c].nOut.value = (genotype.connections[c].nOut.value + (genotype.connections[c].nIn.value*genotype.connections[c].weight))
			
		# put all output values in a single list and return
		outputs = [activate_scoop(x) for x in genotype.nodes[-genotype.numOut:]]
		
		return outputs

def activate_scoop(node):
	"""Top level function for activating a nodes value 
	because scoop must be able to pickle the function.

	Parameters:
	node -- node within the CPPN whose value is being 
	activated
	"""

	val = node.value
	if(node.actKey == 0):
		val = stepAct(val)
	elif(node.actKey == 1):
		val = sigAct(val)
	elif(node.actKey == 2):
		val = reluAct(val)
	elif(node.actKey == 3):
		val = sinAct(val)
	elif(node.actKey == 4):
		val = gaussAct(val)
	elif(node.actKey == 5):
		val = logAct(val)
	elif(node.actKey == 6):
		val = tanhAct(val)
	elif(node.actKey == 7):
		val = squareAct(val)
	elif(node.actKey == 8):
		val = absAct(val)
	return val
