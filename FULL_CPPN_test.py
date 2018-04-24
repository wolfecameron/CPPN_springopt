from FULL_CPPN_node import Node
from FULL_CPPN_con import Connection
from FULL_CPPN_struct import Genotype

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


print("\n")
print("***** RESULT: " + str(failedTests) + " TESTS FAILED *****")