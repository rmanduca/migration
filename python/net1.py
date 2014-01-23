"""
Program to try out importing data and running some stats in network X
"""
import os
import networkx as nx
import pandas as pd

'''
import numpy as np
import geopy as gp
from urllib2 import urlopen
import time
import json
'''
os.chdir("/Users/Eyota/projects/thesis")

gm = pd.io.parsers.read_csv("output/grossm_abridged0910.csv")
gmsub = gm[['source','target','exmptgross']]
gmtuples = [tuple(x) for x in gmsub.values]

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
