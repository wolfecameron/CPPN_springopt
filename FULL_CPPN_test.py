from FULL_CPPN_node import Node

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




print("\n")
print("***** RESULT: " + str(failedTests) + " TESTS FAILED *****")