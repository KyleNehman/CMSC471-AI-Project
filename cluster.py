import math

# keyset is list of all unique tokens
uniqueTokens = {}

# {document_name: {token: normalized_tf.idf}}
corpusVectors = {}

input_dir = ''
output_dir = ''

# Array indices in hash table value arrya
LAST_INPUT_FILE_INDEX = 2
GLOBAL_OCCURENCES_INDEX = 0
DOCUMENT_OCCURENCES_INDEX = 1


# B = (1 + log(f)) * log(N / n)
def calculate_beta(line, global_dict, big_N):
    try:
        args = line.split(': ') # 0 - token, 1 - frequency
        token = args[0]
    
        little_n = global_dict[token][DOCUMENT_OCCURENCES_INDEX]
        freq = args[1]

        a = 1 + math.log(float(freq))
        b = math.log(float(big_N) / float(little_n))
        return a * b
    except:
        return None

# W = B / sqrt(sum of B for every term in doc)^2
def calculate_weight(line, sum_of_squared_betas, global_dict, big_N):
    beta = calculate_beta(line, global_dict, big_N)
    if beta == None:
        return None
    
    return beta / math.sqrt(sum_of_squared_betas)

# freq / totalfreq
def normalize(weight, freq, total_freq):
    if weight == None:
        return None
    
    return float(weight) * (float(freq) / float(total_freq))

# v and w are lists (vectors from a tf.idf matrix)
def cosine(v, w, corpusVectors):
    numerator = 0
    denominator = 0
    vKeys = corpusVectors[v].keys()
    wKeys = corpusVectors[w].keys()
     
    allKeys = {}

    for z in vKeys:
        allKeys[z] = 1
    for z in wKeys:
        allKeys[z] = 1

    vSquared = 0
    wSquared = 0
    
    # if one vector is bigger than another (won't happen)
    # then values of 0 are substituted in
    # this is strictly for good coding practice, and debugging
    for i in allKeys:
        vi = 0
        try:
            vi = corpusVectors[v][i]
            wi = corpusVectors[w][i]
            
            numerator += (vi * wi)
            vSquared += (vi * vi)
            wSquared += (wi * wi)
        except:
            continue
            
    denominator = math.sqrt(vSquared) * math.sqrt(wSquared)

    if denominator == 0:
        return 0
    return numerator / denominator

def genCentroids(bigL):
    centroids = {}
    for i in range(len(bigL)):
        s = 0
        l = len(bigL[i])
        for j in bigL[i]:
            s += j

        s = s / l

        centroids[str(i)] = s
    return centroids

def merge(bigL, k1, k2):
    avg = bigL[k1] + bigL[k2]
    avg = avg / 2

    bigL[str(k1) + " + " + str(k2)] = avg
    bigL.pop(k1, None)
    bigL.pop(k2, None)

    return bigL

def findClosest(bigL):
    pair = (-1, -1)
    dist = 1000
    for key in bigL.keys():
        local = 1000
        z = key
        for k in bigL.keys():
            if key == k:
                continue
            a = abs(bigL[key] - bigL[k])
            if a < local:
                local = a
                z = k
        if local < dist:
            dist = local
            pair = (key, z)
    return pair
def findFarthest(bigL):
    pair = (-1, -1)
    dist = 0
    for key in bigL.keys():
        local = 0
        z = key
        for k in bigL.keys():
            if key == k:
                continue
            a = abs(bigL[key] - bigL[k])
            if a > local:
                local = a
                z = k
        if local > dist:
            dist = local
            pair = (key, z)
    return pair

def cluster(bigL):
    yes = True
    
    while yes:

        yes = False
        for key in bigL.keys():
            if bigL[key] > 0.4:
                yes = True
                break
        if len(bigL.keys()) == 1:
            yes = False
            # "Only one cluster remaining"
            break
        closest = findClosest(bigL)
        if closest[0] == -1:
            yes = False
            break
        # "Merging " + str(closest[0]) + " & " + str(closest[1])
        merge(bigL, closest[0], closest[1])

    return bigL

