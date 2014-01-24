"""
Program to try out importing data and running some stats in network X
"""
import os
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

'''
import numpy as np
import geopy as gp
from urllib2 import urlopen
import time
import json
'''
os.chdir("/Users/Eyota/projects/thesis")

#Import nodes and data
metros = pd.io.parsers.read_csv("output/msadata.csv")
metros = metros.set_index('id')

metros['plat'] = metros['lat'] - 3000
metros['plon'] = -metros['lon'] + 7500

#Put attributes into dictionary form
#For fun, generalize!
def df2rowdict(df, columns):
    dictlist = []
    for i in range(df.shape[0]):
        dictlist.append(makedict(df, df.index[i], columns))
    return dictlist

def makedict(df,row, names):
    return {k: df.loc[row][k] for k in names}

colsOfInterest = ['MSAName','lat','lon','pop']

nodedata = zip(metros.index,df2rowdict(metros,colsOfInterest))

    
#make graph and add nodes
mg = nx.Graph()
mg.add_nodes_from(nodedata)
    
'''
doesn't allow for skipping variables
def makedict(row, names):
    return {names[k]: row[k] for k in range(len(names))}
'''



#Import network edges 
#To add lots of data, have to have a dictionary for each row
gm = pd.io.parsers.read_csv("output/grossm_abridged0910.csv")

gm.set_index(['source','target'],inplace = True)

#Compute gross returns and gross agi
gm['agigross'] = gm[['aggragi_st','aggragi_ts']].apply(min, axis = 1)
gm['retgross'] = gm[['return_st','return_ts']].apply(min, axis = 1)

#Make dictionary of wanted columns
edgeColsofInt = ['exmptgross','agigross','retgross']

#have to make it a three-tuple: first node, second node, dictionary with attributes
edgedata = zip(zip(*gm.index)[0],zip(*gm.index)[1], df2rowdict(gm,edgeColsofInt))

mg.add_edges_from(edgedata)



#Try drawing the network!

lats = nx.get_node_attributes(mg, 'plat')
lons = nx.get_node_attributes(mg, 'plon')
ll = zip(lats.values(), lons.values())
pos = dict(zip(lats.keys(), ll))

pos = dict(zip(metros.index,zip(metros['lon'],metros['lat'])))

plt.figure(figsize = (8,4))
nx.draw(mg, pos = pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)
plt.xlim = (-165,-65)
plt.ylim = (15,65)

plt.savefig("output/firstdraw.jpeg")


#Not sure how to add the data using the add_edges_from command, so going to add it manually
#NBD, but annoying :-/

#Add edges
gmsub = gm[['source','target']]
gmtuples = [tuple(x) for x in gmsub.values]
mg.add_edges_from(gmtuples)



index = pd.MultiIndex.from_arrays([gm['source'],gm['target']], names = ['source','target'])
ngm = gm.set_index(index)
gm.in


t = nx.Graph()
t.add_weighted_edges_from(gmtuples)

#Think this is superfluous. Just merge the individual statistics later
nodes = pd.DataFrame(t.nodes(),columns = ['fips'])
nodes = nodes.set_index('fips')

## Compute degrees, also perhaps centrality measures
deg = t.degree()
wdeg = t.degree(weight = 'weight')

#Add to graph
nx.set_node_attributes(t, 'degree',deg)
nx.set_node_attributes(t, 'wdegree',wdeg)

#Try my log weighted degree

#Try the weighted average of strength and degree like on that website. ~~~


#You can go back and forth between pandas and networkx using the to_dict and from_dict methods

#Put into dataframe for statistics
degdf = pd.DataFrame.from_dict(deg,orient = 'index')
degdf.columns = ['degree']
wdegdf = pd.DataFrame.from_dict(wdeg,orient = 'index')
wdegdf.columns = ['wdegree']

nodes = pd.merge(degdf,wdegdf,left_index = True, right_index = True)
nodes.describe()




#Index by source,target
nidx = pd.MultiIndex.from_arrays([gm['source'],gm['target']], names = ['source','target'])
gm = gm.set_index(nidx)



#First run setup
'''
tracts = pd.io.parsers.read_csv("../raster/output/sample_for_walkscore_5cat.csv")
tracts['snapped_lat'] = ""
tracts['snapped_lon'] = ""
tracts['walkscore'] = ""
k = 0
'''
#In future

tracts = pd.io.parsers.read_csv("raster_walkscores_5cat.csv")
k = tracts[pd.isnull(tracts["snapped_lat"])].index[0]


defurl = 'http://api.walkscore.com/score?format=json&wsapikey=7e26a67a0e7a0c93f66518db621a0272'

for i in range(95):
    idx = i + k
    lat = tracts.loc[idx,'lat']
    lon = tracts.loc[idx,'lon']
    apiurl = defurl + "&lat=" + str(lat) + "&lon=" + str(lon)
    wsreq = urlopen(apiurl)
    wsdat = wsreq.read()
    wsjson = json.loads(wsdat)
    
    tracts.loc[idx,'snapped_lat'] = wsjson['snapped_lat']
    tracts.loc[idx,'snapped_lon'] = wsjson['snapped_lon']
    try: 
        tracts.loc[idx,'walkscore'] = wsjson['walkscore']
    except KeyError:
        tracts.loc[idx,'walkscore'] = '**No Walkscore Available**'
        
    time.sleep(1)

tracts.to_csv('raster_walkscores_5cat.csv', index=False)
