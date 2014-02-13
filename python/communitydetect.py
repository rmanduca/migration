import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import random as rd
import pylab as pl
#import community as cm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot
import com2 as cm

os.chdir("/Users/Eyota/projects/thesis")

year = '0910'

execfile('code/python/importnetworks.py')

coms = metros

#Partition - test
'''
partition = cm.generate_dendogram(mgdraw)
coms = dict2column(coms, partition,'com')
'''

#Take out AK/HI for now for drawing
akhi = metros[(metros['lon'] > -60) | (metros['lon'] <-125)].index
mgdraw = mg.copy()
mgdraw.remove_nodes_from(akhi)
comsdraw = coms[(metros['lon'] < -60) & (metros['lon'] >-125)]

#Projection
project = pyproj.Proj('+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0],t[1])))

'''
nx.draw(nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])['flowcloseness'],
    alpha = .7, linewidths = 0.5, width = 0)


nx.draw(mgdraw, pos,with_labels = False,alpha = 1, linewidths = 0.5, width = 0,
    nodelist = list(comsdraw.sort(['pop']).index),node_size = 40, node_color = comsdraw.sort(['pop'])['com'])

'''

comnet = nx.Graph()
comnet.add_nodes_from(nodedata)

comsdraw = coms[(metros['lon'] < -60) & (metros['lon'] >-125)]
comlist = []
for i in range(10):
    partition = cm.best_partition(mg)
    #I think it's ok to use the full network including AKHI
    comsdraw = dict2column(comsdraw, partition,'com%s'%i)
    #'part%s' %i)
    netplot('output/commaps/maps_com_%s.jpeg'%i,mgdraw,pos,with_labels = False,alpha = 1, linewidths = 0.5, width = 0,
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = comsdraw.sort(['pop'])['com%s'%i])
        
    for n in mg.nodes():
        for m in mg.nodes(): #[find(mg.nodes() == n):len(mg.nodes())]:
            if m == n:
                continue
            else:
                if partition[m] == partition[n]:
                    #comnet.add_edge(m,n)
                    comlist.append((m,n))
        
comdf = pd.DataFrame.from_records(comlist)
comdf['cnt'] = 1
comcol = comdf.groupby([0,1]).agg(sum)
comcol = comcol.sort(['cnt'])
comedges = zip(zip(*comcol.index)[0],zip(*comcol.index)[1],comcol['cnt'])

comnet.add_weighted_edges_from(comedges)
comnetdraw = comnet
comnetdraw.remove_nodes_from(akhi)

elist = [(u,v) for (u,v,d) in comnet.edges(data = True) if d['weight']==10]

#Plot groups that are always in the same network
netplot('output/communities_10.jpg',comnetdraw,pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist
        )        
                
elist_all = zip(zip(*comcol.index)[0],zip(*comcol.index)[1])
#[(u,v) for (u,v,d) in comnet.edges(data = True)]
ecol = comcol['cnt']**2
#.apply(^2, axis = 1
#[d['weight'] for (u,v,d) in comnet.edges(data = True)]

#Plot with weights that depend on number of overlapping communities
netplot('output/communities_10_squared.jpg',comnetdraw,pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist_all,
        edge_color = ecol,
        edge_cmap = pl.cm.Greys
        )   
 
 
ecol = comcol['cnt']
#.apply(^2, axis = 1
#[d['weight'] for (u,v,d) in comnet.edges(data = True)]

#Plot with weights that depend on number of overlapping communities
netplot('output/communities_10_lin.jpg',comnetdraw,pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist_all,
        edge_color = ecol,
        edge_cmap = pl.cm.Greys
        )   
  
#nx.draw(mgdraw, pos,with_labels = False,alpha = .7, linewidths = 0.5, width = 0)