from FULL_CPPN_node import Node
from FULL_CPPN_con import Connection
from FULL_CPPN_struct import Genotype
from FULL_CPPN_evalg import applyWeightMutation
import copy

'''
Helper method for printing out the results of a test to user
prints out all test information to user - result and number 
@param result boolean value for result of test
@param num value for the number of test being run
@param testsFailed total number of tests failed so far
@return totalTests failed after running this test
'''
def printTestResults(result, num, testsFailed):
	if(result):
		print("Passed test " + str(num) + ".")
	else:
		print("***** FAILED TEST " + str(num) + " *****")
		testsFailed += 1
	return testsFailed


# tests for node class below
initNum = 2
initVal = 100
initLayer = 0
initAct = 3

# test variables used throughout tests
failedTests = 0
testNum = 1

print("***** RUNNING CPPN TESTS *****")
print("\n")
print("***** RUNNING NODES TESTS *****")
print("\n")

n1 = Node(initNum, initVal, initLayer, initAct)

# test node accessor methods 
result = n1.getNodeNum() == initNum
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

result = n1.getNodeValue() == initVal
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

result = n1.getNodeLayer() == initLayer
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

result = n1.getActKey() == initAct
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# test node mutator methods
newValue = 5
n1.setNodeNum(newValue)
result = n1.getNodeNum() == newValue
failedTests = printTestResults(result, testNum, failedTests)
n1.setNodeNum(initNum) #change back for later test
testNum += 1

n1.setNodeValue(newValue)
result = n1.getNodeValue() == newValue
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

n1.setNodeLayer(newValue)
result = n1.getNodeLayer() == newValue
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

n1.setActKey(newValue)
result = n1.getActKey() == newValue
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# test equals method
result = n1 == n1
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

nOther = Node(initNum,initVal,initLayer, initAct)
result = n1 == nOther
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

nOther.setNodeNum(1000)
result = not(n1 == nOther)
failedTests = printTestResults(result,testNum, failedTests)
testNum += 1

print("\n")
print("***** RUNNING CONNECTION TESTS *****")
print("\n")

initNum1 = 2
initNum2 = 4
initVal1 = 100
initVal2 = 150
initLayer1 = 0
initLayer2 = 1
initAct1 = 3
initAct2 = 2

conWeight = -3.5
innovNum = 5

n1 = Node(initNum1, initVal1, initLayer1, initAct1)
n2 = Node(initNum2, initVal2, initLayer2, initAct2)
connect1 = Connection(n1,n2,conWeight,innovNum)

# test accessor methods 
result = connect1.getNodeIn() == n1
failedTests = printTestResults(result,testNum, failedTests)
testNum += 1

result = connect1.getNodeOut() == n2
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

result = connect1.getWeight() == conWeight
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

result = connect1.getStatus() == True
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

result = connect1.getInnovationNumber() == innovNum
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

#test mutator methods (make sure to undo changes after)
connect1.setNodeIn(n2)
result = connect1.getNodeIn() == n2
failedTests = printTestResults(result,testNum,failedTests)
connect1.setNodeIn(n1)
testNum += 1

connect1.setNodeOut(n1)
result = connect1.getNodeOut() == n1
failedTests = printTestResults(result,testNum,failedTests)
connect1.setNodeOut(n2)
testNum += 1

newWeight = -100
connect1.setWeight(newWeight)
result = connect1.getWeight() == newWeight
failedTests = printTestResults(result,testNum,failedTests)
connect1.setWeight(conWeight)
testNum += 1

connect1.setStatus(False)
result = connect1.getStatus() == False
failedTests = printTestResults(result,testNum,failedTests)
connect1.setStatus(True)
testNum += 1

#test equals method
connect2 = Connection(n1,n2,conWeight,innovNum)
result = connect1.__eq__(connect2)
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

connect3 = Connection(n1,n2,conWeight + 1, innovNum)
result = connect1.__eq__(connect3)
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

connect4 = Connection(n2,n1, conWeight,innovNum)
result = not(connect1.__eq__(connect4))
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

print("\n")
print("***** RUNNING GENOTYPE TESTS *****")
print("\n")

# size tests
g1 = Genotype(2,1)
result = (g1.size() == 4)
failedTests = printTestResults(result,testNum, failedTests)
testNum += 1

g2 = Genotype(100,200)
result = (g2.size() == 301)
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

# connection tests
result = len(g1.getConnections()) == 3
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

result = len(g2.getConnections()) == 20200
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# node tests
result = len(g1.getNodes()) == 4 
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

result = len(g2.getNodes()) == 301
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

'''
# the following contains a few simple networks printed for verification purposes
# comment out to print less information
g1 = Genotype(2,1)
g2 = Genotype(2,1)
g3 = Genotype(2,1)
print(g1)
print(g2)
print(g3)
'''

# activation/getOutput tests
# these tests depend on weights used in the network, truly verify test through examination
numIn = 2
numOut = 1
g1 = Genotype(numIn,numOut)
out = g1.getOutput([1,1])
result = len(out) == numOut
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1
#print(g1)
#print(out[0])

numOut = 3
g1 = Genotype(numIn,numOut)
out = g1.getOutput([2,2])
result = len(out) == numOut
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1
'''
print(g1)
print("Outputs:")
for o in out:
	print(o)
'''

# node mutations tests
# check to make sure it updates innovation map and global innovation
numIn = 2 
numOut = 1
g1 = Genotype(numIn,numOut)
oldLength = len(g1.nodes)
innovNum = 0
innovMap = {}
updates = g1.nodeMutate(innovMap, 0)
result = g1.size() > oldLength
innovMap = updates[0]
innovNum = updates[1]
result = result and len(innovMap.keys()) == 2
result = result and innovNum == 2
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# check connection info of first node mutation
result = True
for con in g1.connections:
	if(not con.getStatus()):
		inNode = con.getNodeIn().getNodeNum()
		outNode = con.getNodeOut().getNodeNum()
		#print("Node In: " + str(inNode))
		#print("Node Out: " + str(outNode))
		for k in innovMap.keys():
			result = result and (inNode in k or outNode in k)
			#print("new con: " + str(k))
failedTests = printTestResults(result, testNum, failedTests)
g1.getOutput([100,100])
testNum += 1
#print(g1)

# check weights stay same as before
'''
g1 = Genotype(2,1)
print(g1)
g1.nodeMutate(innovMap, innovNum)
print(g1)
print("CHECK THAT WEIGHTS ABOVE STAY SAME GOING IN AND EQUAL 1 GOING OUT")
'''

# check weight mutation method
g1 = Genotype(100,1)
gcopy = g1.getCopy()
g1.weightMutate()
result = False
for x,y in zip(gcopy.connections,g1.connections):
	if(not x.getWeight() == y.getWeight()):
		result = True
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

g1 = Genotype(2,1)
print(g1)
g1.weightMutate()
print(g1)
print("CHECK THAT ALL WEIGHTS WERE CHANGED")

# activation mutation tests
g1 = Genotype(100,1)
gcopy = g1.getCopy()
g1.activationMutate()
result = False
count = 0
for x,y in zip(g1.nodes,gcopy.nodes):
	if(not x.getActKey() == y.getActKey()):
		result = True
		count += 1
result = result and count == 1 or (not result and count == 0)
failedTests = printTestResults(result,testNum,failedTests)
testNum += 1

# valid connection test
g1 = Genotype(4,1)
c1 = Connection(g1.nodes[0],g1.nodes[1], 0,0)
c2 = Connection(g1.nodes[5], g1.nodes[0],-1,0)
result = not g1.validConnection(c1)
result = result and not g1.validConnection(c2)
failedTests = printTestResults(result,testNum,failedTests)

g1.nodeMutate(innovMap,0)
g1.connections = []
c3 = Connection(g1.nodes[6],g1.nodes[0], -1, 0)
c4 = Connection(g1.nodes[6],g1.nodes[5], 1, 0)
result = not g1.validConnection(c3)
result = result and g1.validConnection(c4)
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# connection mutation tests
innovMap = {}
innovNum = 4
g1 = Genotype(3,1)
innovNum = g1.nodeMutate(innovMap, innovNum)[1]
innovNum = g1.nodeMutate(innovMap, innovNum) [1]
print(g1)
innovNum = g1.connectionMutate(innovMap, innovNum)[1]
innovNum = g1.connectionMutate(innovMap, innovNum) [1]
print(g1)
print("CHECK THAT CONNECTIONS WERE ADDED PROPERLY.  INNOV NUMS SHOULD BE ALL UNIQUE")

result = input("DID TESTS PASS? (y/n)")
result = not (result == 'n' or result == 'N')
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# crossover tests
innovNum = 4
g1 = Genotype(2,1)
g1.setFitness(100)
g2 = Genotype(2,1)
g2.setFitness(0)
g3 = g1.crossover(g2)
g1.nodeMutate(innovMap,innovNum)
g3 = g1.crossover(g2)
print(g1)
print(g3)
print("CHECK THAT CONNECTIONS SWITCHED INTITALLY AND NONE OF EXCESS CONNECTIONS CHANGED.")

result = input("DID TESTS PASS? (y/n)")
result = not (result == 'n' or result == 'N')
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# tests for distance method and helper methods
g1 = Genotype(1,1)
avg = g1.getAverageWeight()
totalW = 0.0
totalC = 0.0
for c in g1.connections:
	totalW += c.getWeight()
	totalC += 1
result = avg == (totalW/totalC)
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

g1 = Genotype(100,1)
avg = g1.getAverageWeight()
totalW = 0.0
totalC = 0.0
for c in g1.connections:
	totalW += c.getWeight()
	totalC += 1
result = avg == (totalW/totalC)
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

g1 = Genotype(2,1)
innovTup = g1.findRangeOfInnovationNumbers()
print(innovTup)
result = innovTup[0] == 0 and innovTup[1] == 2
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

innovNum = 3
innovNum = g1.nodeMutate(innovMap, innovNum)[1]
innovNum = g1.nodeMutate(innovMap, innovNum)[1]
innovNum = g1.nodeMutate(innovMap, innovNum)[1]
innovNum = g1.nodeMutate(innovMap, innovNum)[1]
innovTup = g1.findRangeOfInnovationNumbers()
print(g1)
print("HERE IS THE INNOVATION MIN MAX RETURNED BY METHOD: " + str(innovTup))
result = input("DID TESTS PASS? (y/n)")
result = not (result == 'n' or result == 'N')
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

# extra activation tests
g1 = Genotype(2,1)
g1.nodeMutate(innovMap, innovNum)
g1.nodeMutate(innovMap, innovNum)
g1.connectionMutate(innovMap, innovNum)
print(g1)
print(g1.getOutput([2,3]))

# extra weight mutation tests
size = 3
gens = []
for x in range(size):
	gens.append(Genotype(1,1))
gens_og = copy.deepcopy(gens)
for org in gens:
	org.weightMutate()
result = True

# check all weights are different 
for orgInd in range(len(gens)):
	org1 = gens[orgInd]
	org2 = gens_og[orgInd]
	for cInd in range(len(org1.connections)):
		con1 = org1.connections[cInd]
		con2 = org2.connections[cInd]
		if(con1.getWeight() == con2.getWeight()):
			result = False
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1


gens = []
for x in range(size):
	gens.append(Genotype(1,1))
gens_og = copy.deepcopy(gens)
for org in gens:
	applyWeightMutation(gens, 1.0)
result = True

# check all weights are different 
for orgInd in range(len(gens)):
	org1 = gens[orgInd]
	org2 = gens_og[orgInd]
	for cInd in range(len(org1.connections)):
		con1 = org1.connections[cInd]
		con2 = org2.connections[cInd]
		if(con1.getWeight() == con2.getWeight()):
			result = False
failedTests = printTestResults(result, testNum, failedTests)
testNum += 1

print("\n")
print("***** RESULT: " + str(failedTests) + " TESTS FAILED *****")