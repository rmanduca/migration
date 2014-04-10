"""
Make a basic map of the migration network of the US
"""

import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
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

#Basic network
metros, mg, nodedata = importnetwork(year)

#Prepare for drawing
#remove AKHI
akhi = metros[(metros['lon'] > -60) | (metros['lon'] <-125)].index
metrosdraw = metros[(metros['lon'] < -60) & (metros['lon'] >-125)]
mgdraw = mg.copy()
mgdraw.remove_nodes_from(akhi)

#Project
project = pyproj.Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=38.5 +lon_0=-97 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
t = project(metrosdraw['lon'],metrosdraw['lat'])
pos = dict(zip(metrosdraw.index,zip(t[0]+width / 2,t[1] + height / 2)))

elist = [(u,v) for (u,v,d) in mgdraw.edges(data = True)]
ew = [(d['exmptgross']) for (u,v,d) in mgdraw.edges(data = True)]
edges = pd.DataFrame(elist)
edges['weight'] = ew

edges.sort('weight', inplace = True, ascending = False)
edges['lw'] = edges['weight'].apply(log)
elist_sort = zip(edges[0],edges[1])

greys = cm = plt.get_cmap('gray') 
cNorm  = colors.Normalize(vmin=0, vmax=max(ew))
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    
netplot('output/test.pdf',width, height, mgdraw, pos, with_labels = False, 
    nodelist = list(metrosdraw.sort(['pop']).index), 
    node_size = sqrt(metrosdraw.sort(['pop'])['pop'])/15, 
    node_color = 'black', edge_list = elist_sort, edge_color = edges['weight'], edge_cmap = greys,
    alpha = .8, linewidths = 1, width = 0.5)



nx.draw_networkx_edges(mgdraw,pos, with_labels = False, 
     edge_list = elist_sort, edge_color = edges['weight'], edge_cmap = greys,
    alpha = .8, linewidths = 0.5, width = 0.5)


   nx.draw(G,edge_color=colorList)
\
G = nx.Graph() 
G.add_edge(1, 2, weight=3) 
G.add_edge(2, 3, weight=50) 
nx.draw(G) 
netplot('output/communities_95_%s.pdf' %year,width, height, comnetdraw,pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist
        )  