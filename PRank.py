import os
import numpy

def getGraphAsMatrix(fileName):
    dimension = 0
    graphFile = open(fileName, "r")
    lines = graphFile.readlines()
    lines.sort()
    graphFile.close()
    lastLine = lines[len(lines)-1] #! we need the last index 
    lastNode = lastLine.split()[0] #! in a line we have 2 node which is separated by space
    dimension = int(lastNode)+1 #! node started with 0  
    graphAsMatrix = numpy.zeros([dimension, dimension], float) #! we initial our matrix first

    for line in lines: #! fill our matrix with 1 corresponding to the start node and pointed node
        nodes = line.split()
        startNode = int(nodes[0]) 
        pointedNode = int(nodes[1]) 
        graphAsMatrix[startNode, pointedNode] = 1 
    return graphAsMatrix

def getOutLinkVectorSize(graphAsMatrix): #! find number of outlinks for each node
    outLinkVectorSize = numpy.sum(graphAsMatrix, axis = 1)
    return outLinkVectorSize

def getInLinkVectorSize(graphAsMatrix): #! find number of inlinks for each node
    inLinkVectorSize = numpy.sum(graphAsMatrix, axis = 0)
    return inLinkVectorSize

def LookUpScore(node_1, node_2, iterationNo): #! read a calculated score from an according file
    fileName = "ResultOnIteration_" + str(iterationNo)
    graphFile = open(fileName, "r")
    lines = graphFile.readlines()
    lines.sort()
    graphFile.close()
    for line in lines: #! read line by line until we find them
        firstnode = line.split(",")[0]
        pointedNodeAndScore = line.split(",")[1]
        pointedNode = pointedNodeAndScore.split(" :")[0]
        score = pointedNodeAndScore.split(":")[1].split("\n")[0]
        if node_1 == int(firstnode) and node_2 == int(pointedNode):
            return score
    return 0
       
def computePRankSimilarity(graphAsMatrix, similarityScoreMatrix, iteration, currentIteration = 1):
    if iteration == 0:
        return similarityScoreMatrix
    elif iteration <= 5 and iteration > 0:
        print("This is iteration " + str(currentIteration))
        constant = 0.8
        beta = 0.5
        dimension = len(similarityScoreMatrix)
        outLinkVectorSize = getOutLinkVectorSize(graphAsMatrix)
        inLinkVectorSize = getInLinkVectorSize(graphAsMatrix)
        tempScoreMatrix = similarityScoreMatrix.copy() #! for keeping new calculated scores
        for nodePIndex in range(dimension):
            nodePInLinkVector = graphAsMatrix[:,nodePIndex] #! get only column for P
            nodePOutLinkVector = graphAsMatrix[nodePIndex]  #! get only row for P
            for nodeQIndex in range(dimension):
                nodeQInLinkVector = graphAsMatrix[:,nodeQIndex] #! get only column for Q
                nodeQOutLinkVector = graphAsMatrix[nodeQIndex] #! get only row for Q
                if nodePIndex != nodeQIndex: #! if they are not the same nodes , we need to compute the score
                    nodePInLinkIndices = numpy.where(nodePInLinkVector == 1)[0] #! find which node pointing to P
                    nodeQInLinkIndices = numpy.where(nodeQInLinkVector == 1)[0] #! find which node pointing to Q
                    nodePOutLinkIndices = numpy.where(nodePOutLinkVector == 1)[0] #! find which node P pointing to
                    nodeQOutLinkIndices = numpy.where(nodeQOutLinkVector == 1)[0] #! find which node Q pointing to
                    if(inLinkVectorSize[nodePIndex] != 0 and inLinkVectorSize[nodeQIndex] != 0): #! there are the divisors, must be > 0
                        prefixInLink = (constant*beta) / (inLinkVectorSize[nodePIndex] * inLinkVectorSize[nodeQIndex])
                    else:
                        prefixInLink = 0
                    if(outLinkVectorSize[nodePIndex] != 0 and outLinkVectorSize[nodeQIndex] != 0): #! there are the divisors, must be > 0
                        prefixOutLink = (constant*(1 - beta)) / (outLinkVectorSize[nodePIndex] * outLinkVectorSize[nodeQIndex])
                    else:
                        prefixOutLink = 0
                    postfixInLink = 0  
                    postfixOutLink = 0
                    for nodePInLinkIndex in nodePInLinkIndices: #! compute the sum of similarity for Inlinknode of P and Q 
                            for nodeQInLinkIndex in nodeQInLinkIndices: 
                                    postfixInLink += similarityScoreMatrix[nodePInLinkIndex][nodeQInLinkIndex]
                    for nodePOutLinkIndex in nodePOutLinkIndices: #! compute the sum of similarity for Outlinknode of P and Q
                            for nodeQOutLinkIndex in nodeQOutLinkIndices: 
                                    postfixOutLink += similarityScoreMatrix[nodePOutLinkIndex][nodeQOutLinkIndex]
                    score = (prefixInLink * postfixInLink) + (prefixOutLink * postfixOutLink) #! compute similarity score for P and Q
                    if score != 0 : 
                        newfile = open("ResultOnIteration_" + str(currentIteration), "a")
                        roundedScore = numpy.round(score, decimals = 5)
                        if roundedScore == 0:  #! In case we get score != 0 but <= 0.000005
                            roundedScore = 0.000005 #!
                        newfile.write(str(nodePIndex) + "," + str(nodeQIndex) + " :" + "{:.5f}".format(roundedScore)) #! show 5 decimals point
                        newfile.write("\n")
                        newfile.close()
                    tempScoreMatrix[nodePIndex][nodeQIndex] = score #! update new calculated scores here
                else:
                    score = 1
                    newfile = open("ResultOnIteration_" + str(currentIteration), "a")
                    newfile.write(str(nodePIndex) + "," + str(nodeQIndex) + " :" + "{:.5f}".format(score))
                    newfile.write("\n")
                    newfile.close()
                    # print(str(1000 - nodePIndex) + " Node(s) left to compute in Iteration " + str(currentIteration))
        return computePRankSimilarity(graphAsMatrix, tempScoreMatrix, iteration - 1, currentIteration + 1)

#*-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*#

threshold = 3
if os.path.isfile('./ResultOnIteration_1') and os.path.isfile('./ResultOnIteration_2') and os.path.isfile('./ResultOnIteration_3'):
    Isexit = "no"
    while Isexit != "yes":
        print("------------------------------------------------------------")
        print("The score have been computed, you can look up for the score!")
        print("------------------------------------------------------------")
        inputLength = 0
        while inputLength != 3:
            lookUpInput = input("Enter 'node_1 node_2 iteration' to lookup the score: ")
            inputLength = len(lookUpInput.split())
            if inputLength != 3:
                print("The input needed to be in this format: 'node_1 node_2 iteration'")     
        node1 = int(lookUpInput.split()[0])
        node2 = int(lookUpInput.split()[1])
        iteration = int(lookUpInput.split()[2])
        if iteration == 0:
            if node1 != node2:
                score = 0
                print(score)
                Isexit = input("Type 'yes' to exit: ")
            else:
                score = 1
                print(score)
                Isexit = input("Type 'yes' to exit: ")
        elif iteration <= 5 and iteration > 0:
            if node1 == node2:
                score = 1
                print(score)
                Isexit = input("Type 'yes' to exit: ")
            else:
                score = LookUpScore(node1,node2,iteration)
                print(score)
                Isexit = input("Type 'yes' to exit: ")
        else:
            print("Iteration must be between 0 and 5")
            Isexit = input("Type 'yes' to exit: ")

elif os.path.isfile('./ResultOnIteration_1') or os.path.isfile('./ResultOnIteration_2') or os.path.isfile('./ResultOnIteration_3'):
    print("------------------------------------------------------------")        
    print("Please remove all the existing results files and run the program agian")
    print("------------------------------------------------------------")    
else:
    print("------------------------------------------------------------")    
    print("You need to compute the score first")
    print("------------------------------------------------------------")
    myFirstInput = " "
    while myFirstInput != "compute":
        myFirstInput = input("Please type 'compute' to start the programe: ")
    myFileName = "graph.txt"
    myGraphAsMatrix = getGraphAsMatrix(myFileName) #! read file
    dimension = len(myGraphAsMatrix) 
    myinitialSimilarityScoreMatrix =  numpy.zeros([dimension, dimension], float)
    numpy.fill_diagonal(myinitialSimilarityScoreMatrix, float(1)) #! the same nodes have similarity score equal 1 
    myFinalIterationSimilarityScore = computePRankSimilarity(myGraphAsMatrix, myinitialSimilarityScoreMatrix, threshold)

    Isexit = "no"
    while Isexit != "yes":
        print("------------------------------------------------------------")
        print("The score have been computed, you can look up for the score!")
        print("------------------------------------------------------------")
        inputLength = 0
        while inputLength != 3:
            lookUpInput = input("Enter 'node_1 node_2 iteration' to lookup the score: ")
            inputLength = len(lookUpInput.split())
            if inputLength != 3:
                print("The input needed to be in this format: 'node_1 node_2 iteration'")     
        node1 = int(lookUpInput.split()[0])
        node2 = int(lookUpInput.split()[1])
        iteration = int(lookUpInput.split()[2])
        if iteration == 0:
            if node1 != node2:
                score = 0
                print(score)
                Isexit = input("Type 'yes' to exit: ")
            else:
                score = 1
                print(score)
                Isexit = input("Type 'yes' to exit: ")
        elif iteration <= 5 and iteration > 0:
            if node1 == node2:
                score = 1
                print(score)
                Isexit = input("Type 'yes' to exit: ")
            else:
                score = LookUpScore(node1,node2,iteration)
                print(score)
                Isexit = input("Type 'yes' to exit: ")
        else:
            print("Iteration must be between 0 and 5")
            Isexit = input("Type 'yes' to exit: ")






