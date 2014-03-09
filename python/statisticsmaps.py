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
width = 4700000
height = 3100000

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
project = pyproj.Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=38.5 +lon_0=-97 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')

t = project(statsdraw['lon'],statsdraw['lat'])
pos = dict(zip(statsdraw.index,zip(t[0]+width / 2,t[1] + height / 2)))


#Loop through statistics
for stat in ['degree','wdegree','closeness','flowcloseness','btwnness','flowbtwnness']:
    netplot('output/maps_%s.jpeg' %stat,width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])[stat],
    alpha = .7, linewidths = 0.5, width = 0)




#Plot statistics vs each other
plt.plot(stats['pop'],stats['wdegree'], 'bo')

plt.figure()
plt.plot(log(stats['pop']),stats['flowcloseness'], 'bo')

plt.figure()
plt.plot(log(stats['wdegree']),stats['flowcloseness'], 'bo')

plt.figure()
plt.plot(stats['pop'],stats['flowbtwnness'], 'bo')

plt.figure()
plt.plot(log(stats['pop']),log(stats['flowbtwnness']), 'bo')

plt.figure()
plt.plot(stats['flowcloseness'],log(stats['flowbtwnness']), 'bo')
plt.axis([0,600,-15,0])
plt.savefig('output/correlations/closebtwn.jpeg')
plt.close()

plt.figure()
plt.plot(stats['flowcloseness'],(stats['flowbtwnness']), 'bo')
plt.savefig('output/correlations/closebtwn_lin.jpeg')
plt.close()

plt.figure()
plt.plot(log(stats['wdegree']),log(stats['flowbtwnness']), 'bo')



#Try drawing - degree

netplot('output/maps_degree.jpeg',width, height, mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])['degree'],
    alpha = .7, linewidths = 0.5, width = 0)

netplot('output/maps_flowclose.jpeg',mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])['flowcloseness'],
    alpha = .7, linewidths = 0.5, width = 0)

netplot('output/maps_eigenvc.jpeg',mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])['eigenvc'],
    alpha = .7, linewidths = 0.5, width = 0)

netplot('output/maps_weigenvc.jpeg',mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = sqrt(statsdraw.sort(['pop'])['weigenvc']),
    alpha = .7, linewidths = 0.5, width = 0)

plt.figure(figsize = (15,11))
nx.draw(mgdraw, pos = pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])['degree'],
    alpha = .7, linewidths = 0.5, width = 0)
plt.axis([-2300000,2100000, -1800000, 1500000])


#pos = dict(zip(metros.index,zip(metros['lon'],metros['lat'])))

t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0],t[1])))






nx.draw(mg, pos = pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)







netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

nx.draw(mg, pos = pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)
