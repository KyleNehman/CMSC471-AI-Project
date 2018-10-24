import os
import nltk
from preProcess import getFilteredData

from cluster import calculate_beta
from cluster import genCentroids
from cluster import normalize
from cluster import calculate_weight
from cluster import findFarthest
from cluster import findClosest
from cluster import cosine
from cluster import cluster


# Global map of {token: [global_occurences, num_docs, last_input_file]}
globalDict = {}

# {document_name: {token: normalized_tf.idf}}
corpusVectors = {}

# Array indices in hash table value arrya
LAST_INPUT_FILE_INDEX = 2
GLOBAL_OCCURENCES_INDEX = 0
DOCUMENT_OCCURENCES_INDEX = 1


# Since we have to examine the entire corpus we must compare documents.
# To avoid storing the whole 700+ documents in memory we will use staging files
# That represent their individual hash maps of token to number of occurences.i
def writeToStagingFile(map, fileName):
    stagingFile = open("staging/" + fileName + ".staging", "w")

    for key in map.keys():
        stagingFile.write(str(key) + ": " + str(map[key]) + "\n")

    stagingFile.close()

def main():
    try:
        os.mkdir("staging")
    except:
        x = None #Ignoring an exception here

    # Loop all documents, add tokenized data to maps and 
    # Temporary staging files.
    numDocuments = 0
    for fileName in os.listdir("input"):
        validWords = {}
        docTokens = getFilteredData("input/" + fileName)
        docTags = nltk.pos_tag(docTokens)

        numDocuments += 1
        for token in docTags:
            part = token[1]
            word = token[0]

            # If is verb or noun add to local and global maps
            if "VB" in part or "NN" in part:

                # Local
                if validWords.get(word) == None:
                    validWords[word] = 1
                else:
                    validWords[word] += 1

                # Global + "metadata"
                if globalDict.get(token) != None:
                    globalDict[token][GLOBAL_OCCURENCES_INDEX] += 1

                    # Have to keep track of the last input file in order to track the number of documents token occurs in.
                    if globalDict[token][LAST_INPUT_FILE_INDEX] != fileName:
                        globalDict[token][DOCUMENT_OCCURENCES_INDEX] += 1
                        globalDict[token][LAST_INPUT_FILE_INDEX] = fileName
                    
                else:
                    globalDict[token] = []
                    
                    globalDict[token].append(1) # global count
                    globalDict[token].append(1) # document occurences count
                    globalDict[token].append(fileName) # last edited file count

        writeToStagingFile(validWords, fileName)

    # Start processing now that each document has been examined once
    documentNames = []
    for fileName in os.listdir("staging"):
        stagingFile = open("staging/" + fileName, "r")
        lines = stagingFile.readlines()

        sum_of_squared_betas = 0
        total_freq = 0
        for line in lines:
            freq = int(line.split(': ')[1])
            beta = calculate_beta(line, globalDict, numDocuments)
            if beta == None:
                continue
            
            sum_of_squared_betas = beta * beta
            total_freq += freq
        
        stagingFile.close()
        os.remove("staging/" + fileName)

        documentNames.append(fileName) 
        corpusVectors[fileName] = {}
        for line in lines:
            split = line.split(': ')
            token = split[0]
            freq  = split[1]
            
            weight = calculate_weight(line, sum_of_squared_betas, globalDict, numDocuments)
            weight = normalize(weight, freq, total_freq)

            corpusVectors[fileName][token.lower()] = weight
   

    # Start real simularity and clustering calculations!
    simMatrix = []

    for i in range(numDocuments):
        inner = []
        for j in range(numDocuments):
            inner.append(0)
        simMatrix.append(inner)
        
    for i in range(numDocuments):
        v = documentNames[i]
        for j in range(i, numDocuments):
            w = documentNames[j]
            cs = cosine(v, w, corpusVectors)
            simMatrix[i][j] = cs

    centroids = genCentroids(simMatrix)
    bigL = cluster(centroids)

main()
