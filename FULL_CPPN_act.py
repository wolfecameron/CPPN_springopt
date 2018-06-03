import numpy as np
'''
This file contains various activation functions, stored within CPPN nodes
All activations have a chance to be stored within a node
Output is always step function - all other nodes can have any activation function
'''

#step function activation
def stepAct(x):
	if(x>.5):
		return 1;
	else:
		return 0;

#sigmoid activation function
def sigAct(x):
	steepnessCoefficient = 4.9
	return float(1)/(1+np.exp(-steepnessCoefficient*x))
		
#ReLU activation function (linear if greater than 0, else 0)
def reluAct(x):
	return 0 if x<0 else x
	
#sin function (using numpy)	
def sinAct(x):
	return np.sin(x)

# gaussian activation function
# returns sample from normal distrib u = x, var = 1
def gaussAct(x):
	variance = 1.0
	return np.random.normal(x,variance)

#logistic activation function
# not defined for x < 0, anything x val below 0 returns 0
def logAct(x):
	if(not (x > 0)):
		return 0
	return np.log(x)

# tanh activation function
def tanhAct(x):
	return np.tanh(x)

# square activation function
def squareAct(x):
	return x**2

# absolute value activation function
def absAct(x):
	return abs(x)



