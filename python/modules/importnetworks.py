"""
Program to read in migration data into a network file.
Now written as a module with a function taking a year of '0405' - '0910'
"""
import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import df2rowdict, makedict
from drawnetworks import netplot

os.chdir("/Users/Eyota/projects/thesis")


def importnetwork(year):
    
    #Import nodes and data
    #Note: Includes Puerto Rico Metros that don't have migration data
    metros = pd.io.parsers.read_csv("output/msadata.csv")
    metros = metros.set_index('id')
    
    #Remove nodes for Puerto Rico based on identification at bottom of this script
    prlist = [10260, 46580, 10380, 25020, 32420, 41900, 41980, 17620, 42180, 21940, 27580, 49500, 38660]
    metros = metros.drop(prlist)
    
    colsOfInterest = ['MSAName','lat','lon','pop']
    
    nodedata = zip(metros.index,df2rowdict(metros,colsOfInterest))
    
    #make graph and add nodes
    mg = nx.Graph()
    mg.add_nodes_from(nodedata)
    
    
    #Import network edges 
    #To add lots of data, have to have a dictionary for each row
    gm = pd.io.parsers.read_csv("output/grossm_abridged%s.csv" %year)
    
    gm.set_index(['source','target'],inplace = True)
    
    #Compute gross returns and gross agi
    gm['agigross'] = gm[['aggragi_st','aggragi_ts']].apply(min, axis = 1)
    gm['retgross'] = gm[['return_st','return_ts']].apply(min, axis = 1)
    
    #Make dictionary of wanted columns
    edgeColsofInt = ['exmptgross','agigross','retgross']
    
    #have to make it a three-tuple: first node, second node, dictionary with attributes
    edgedata = zip(zip(*gm.index)[0],zip(*gm.index)[1], df2rowdict(gm,edgeColsofInt))
    
    mg.add_edges_from(edgedata)
    
    return [metros, mg]

'''
#Find PR metros with now nodes
prlist = []
for n in mg:
    if len(mg[n]) == 0:
        prlist.append(n)
        
print metros.loc[prlist]
#all nodes without edges are in Puerto rico
'''