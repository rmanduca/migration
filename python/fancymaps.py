"""
Start doing statistics!

"""

import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import mpl_toolkits.basemap as bm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot
import weighted_eigenvector as we
from importnetworks import importnetwork

os.chdir("/Users/Eyota/projects/thesis")

year = '0910'

metros, mg = importnetwork(year)


#Compute statistics
stats = metros

#Degree
degree = mg.degree()
stats = dict2column(stats, degree, 'degree')

#Weighted Degree
wdegree = mg.degree(weight = 'exmptgross')
stats = dict2column(stats, wdegree, 'wdegree')

#Current Closeness Centrality 
flowcloseness = nx.current_flow_closeness_centrality(mg, weight = 'exmptgross')
stats = dict2column(stats, flowcloseness, 'flowcloseness')

#Vertex Closeness
closeness = nx.closeness_centrality(mg)
stats = dict2column(stats, closeness, 'closeness')

#Vertex Betweenness
btwnness = nx.betweenness_centrality(mg)
stats = dict2column(stats, btwnness, 'btwnness')

#Current Betweenness
flowbtwnness = nx.current_flow_betweenness_centrality(mg, weight = 'exmptgross')
stats = dict2column(stats, flowbtwnness, 'flowbtwnness')

#Eigenvector Centrality
eigenvc = nx.eigenvector_centrality(mg)
stats = dict2column(stats, eigenvc, 'eigenvc')

#Weighted Eigenvector Centrality
weigenvc = we.eigenvector_centrality(mg, weight = 'exmptgross')
stats = dict2column(stats, weigenvc, 'weigenvc')




#Try drawing

#Make new dataframe for drawing that omits Alaska and Hawaii
akhi = metros[(metros['lon'] > -60) | (metros['lon'] <-125)].index
statsdraw = stats[(stats['lon'] < -60) & (stats['lon'] >-125)]

mgdraw = mg.copy()
mgdraw.remove_nodes_from(akhi)

#Play with projections
project = pyproj.Proj('+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')

t = project(statsdraw['lon'],statsdraw['lat'])
pos = dict(zip(statsdraw.index,zip(t[0],t[1])))
pos2 = dict(zip(statsdraw.index,zip(t[0]+3000000,t[1]+2000000)))

#Basemap

m = bm.Basemap(width = 6000000, height = 4000000, projection = 'aea', resolution = 'l', lat_1 = 20, lat_2 = 60, lat_0 = 40, lon_0 = -96)
m.drawcountries()
m.drawcoastlines()
#m.drawstates()
plt.show()

nx.draw(mgdraw,pos2,with_labels = False,alpha = 1, linewidths = 0.5, width = 0,
        nodelist = list(statsdraw.sort(['pop']).index),
        node_size = sqrt(statsdraw.sort(['pop'])['pop'])/3,
        node_color = statsdraw.sort(['pop'])['wdegree'])







netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

nx.draw(mg, pos = pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)
