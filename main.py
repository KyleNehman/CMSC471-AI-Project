from preProcess import getFilteredData
from preProcess import getAllUniqueTokens

from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import ward 
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os

# Computes both a hierarchical agglomerative cluster and a k-means (5) 
def main():
    documents = []
    
    path = "input/stm/"
    numClusters = 5
    clusterColors = {  0: '#FF33D4', 
                        1: '#FCFF33', 
                        2: '#3358FF', 
                        3: '#33FFE3', 
                        4: '#FF5733'
    }

    # Iterate files in the input $path and append to a list of strings
    fileNames = []
    files = os.listdir(path)
    for i in range(0, len(files)):

        doc = ""
        fileName = files[i]
        fileNames.append(fileName)
        file = open(path + fileName, "r")
        lines = file.readlines()
        for line in lines:
            doc += line + "\n"
        documents.append(doc)

    # Build tfidf matrix from documents
    vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
            min_df=0.1, 
            use_idf=True, tokenizer=getFilteredData, ngram_range=(1,3))

    matrix = vectorizer.fit_transform(documents)

    # Get unique tokens, featured names for vocabFrames from docs
    allVocab = getAllUniqueTokens(documents)
    featureNames = vectorizer.get_feature_names()
    vocabFrame = pd.DataFrame({'words': allVocab}, index=allVocab)
   
    # Calc simularity and k-means cluster
    dist = 1 - cosine_similarity(matrix)
    km = KMeans(n_clusters=numClusters)
    km.fit(matrix)
    clusters = km.labels_.tolist()

    # Separate Agglomerative Cluster for comparison
    linkage_matrix = ward(dist) 

    # Generate the dendrogram for the hierarchical cluster 
    fig, ax = plt.subplots(figsize = (20, 33)) 
    ax = dendrogram(linkage_matrix, orientation = "left", labels=fileNames)
    plt.tick_params( axis= 'x', which='both', bottom = 'off', top = 'off', labelbottom='off')
    plt.tight_layout() 

    plt.savefig('agglomerative.png', dpi = 400) 
    plt.close()                          


    # Build labels based on k-means clustered data
    clusterNames = {}
    clusterCenters = km.cluster_centers_.argsort()[:, ::-1]
    for i in range(numClusters):
        topic = ""
        for ind in clusterCenters[i, :3]:
            topic += str(vocabFrame.ix[featureNames[ind].split(' ')].values.tolist()[0][0]) + " "
        
        clusterNames[i] = topic


    # Begin visual representation!
    MDS()
    mds = MDS(n_components = 2, dissimilarity = "precomputed", random_state  =1)
    position = mds.fit_transform(dist)  

    xs, ys = position[:, 0], position[:, 1]
    dataFrame = pd.DataFrame(dict(x = xs, y = ys, label = clusters, title = fileNames)) 
    
    # CSS Borrowed from stackoverflow
    css = """
    text.mpld3-text, div.mpld3-tooltip {
              font-family:Arial, Helvetica, sans-serif;
              }

    g.mpld3-xaxis, g.mpld3-yaxis {
            display: none; }
    """

    fig, ax = plt.subplots(figsize=(14,6)) 
    ax.margins(0.03) 

    # Matplotlibs group labels and axis
    groups = dataFrame.groupby('label')
    for name, group in groups:
        ax.plot(group.x, group.y, marker = 'o', linestyle = '', ms = 12, label = clusterNames[name], color = clusterColors[name], mec = 'none')
        ax.set_aspect('auto')
        ax.tick_params(axis = 'x', which = 'both', bottom = 'off', top = 'off', labelbottom = 'off')
        ax.tick_params(axis = 'y', which = 'both', left = 'off', top = 'off', labelleft = 'off')

    # Set the legend to only use one point
    ax.legend(numpoints=1)  

    # Matplotlibs Labels 
    for i in range(len(dataFrame)):
        ax.text(dataFrame.ix[i]['x'], dataFrame.ix[i]['y'], dataFrame.ix[i]['title'], size=8)  

    # Display K Means
    plt.show() 
main()
