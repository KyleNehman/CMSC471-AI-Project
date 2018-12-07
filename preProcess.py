import nltk

stopList = ["also", "said", "get", "something", "go", "going", "thing", "things", "talk", "talks", "new", "ted", "more", "life", "shows", "people", "us", "world", "the", "applause", "laughter","thank", "i", "is", "was", "what", "a", "ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"]


def valid(word, blackList):
    if len(word) <= 0:
        return False

    part = nltk.pos_tag([word])[0][1]
    return (blackList.get(word) == None) and (word.isalpha()) and ("NN" in part or "VB" in part)

def containsBracket(word):
    total = 0
    ignore = False
    map = {"{": 0, "}": 0, "[": 0, "]": 0, "(": 0, ")": 0, "<": 0, ">": 0}

    for c in word:
        if c in map.keys():
            map[c] += 1
            ignore = True

    total += map["{"]
    total -= map["}"]
    total += map["("]
    total -= map[")"]
    total += map["["]
    total -= map["]"]
    total += map["<"]
    total -= map[">"]
    
    return (total, ignore)

def filter(lines, blackList):
    returnVal = [] 
    
    brackets = 0
    for line in lines.split("\n"):
        for word in line.split(" "):
            tup = containsBracket(word)
            brackets += tup[0]
            if brackets == 0 and not tup[1] and valid(word, blackList):
                returnVal.append(word)

    return returnVal

def getFilteredData(doc):
    blackList = {}
    for word in stopList:
        blackList[word] = 1
   
    return filter(doc, blackList)

def getAllUniqueTokens(documents):
    returnVal = []
    map = {}

    for doc in documents:
        words = getFilteredData(doc)

        for word in words:
            if map.get(word) == None:
                map[word] = 1

    for key in map.keys():
        returnVal.append(key)

    return returnVal
