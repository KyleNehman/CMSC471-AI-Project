import os
import nltk
from preProcess import getFilteredData

nounTags = ['NN', 'NNP', 'NNPS', 'NNS']

for fileName in os.listdir("stm"):
    nouns = {}
    docTokens = getFilteredData("stm/" + fileName)
    docTags = nltk.pos_tag(docTokens)

    for token in docTags:
        if token[1] in nounTags:
            if nouns.get(token[0]) == None:
                nouns[token[0]] = 1
            else:
                nouns[token[0]] += 1
    print(nouns.keys()) # prints just the nouns per doc


