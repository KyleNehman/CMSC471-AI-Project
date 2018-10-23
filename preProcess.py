import os

def valid(word, blackList):
    return blackList.get(word) == None and not any(char.isdigit() for char in word)

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
    for line in lines:
        for word in line.split(" "):
            tup = containsBracket(word)
            brackets += tup[0]
            if brackets == 0 and not tup[1] and valid(word, blackList):
                returnVal.append(word)

    return returnVal

def getFilteredData(fileName):
    file = open(fileName, "r")
    blackList = {fileName: 1}
    
    lines = filter(file.readlines(), blackList)
    print(lines)

for fileName in os.listdir("stm"):
    #print fileName
    getFilteredData("stm/" + fileName)

