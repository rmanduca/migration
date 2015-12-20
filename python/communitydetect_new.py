import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import random as rd
import pylab as pl
import mpl_toolkits.basemap as bm

from numpy import sqrt
#import community as cm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot, netplot_edges
from importnetworks import importnetwork
import com2 as cm

os.chdir("/Users/Eyota/projects/thesis")

year = '0910'
width = 4700000
height = 3100000

metros, mg, nodedata = importnetwork(year)

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
project = pyproj.Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=38.5 +lon_0=-97 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0]+width / 2,t[1] + height / 2)))

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
modularities = []
for i in range(100):
    partition = cm.best_partition(mg)
    modularities.append(cm.modularity(partition, mg))
    #I think it's ok to use the full network including AKHI
    comsdraw = dict2column(comsdraw, partition,'com%s'%i)
    #'part%s' %i)
    netplot('output/commaps/maps_com_%s_%s_new.jpeg'%(i,year),width, height, mgdraw,pos,with_labels = False,alpha = 1, linewidths = 0.5, width = 0,
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

moddf = pd.DataFrame(data = modularities)
moddf.to_csv('output/commaps/modularities_new.csv')

comnet.add_weighted_edges_from(comedges)
comnetdraw = comnet
comnetdraw.remove_nodes_from(akhi)

elist = [(u,v) for (u,v,d) in comnet.edges(data = True) if d['weight'] >=95]

#Plot groups that are always in the same network
netplot('output/communities_95_%s_new.jpg' %year,width, height, comnetdraw,pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist
        )     

#Add in state lines   
plt.figure(figsize = (15,11))
m = bm.Basemap(width = width, height = height, projection = 'aea', resolution = 'l', lat_1 = 29.5, lat_2 = 45.5, lat_0 = 38.5, lon_0 = -97)
m.drawcountries()
m.drawcoastlines()
m.drawstates()
plt.show()    

nx.draw(comnetdraw, pos,with_labels = False,alpha = .1, linewidths = 0, 
        nodelist = list(comsdraw.sort(['pop']).index),
        node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        node_color = 'gray',
        edgelist = elist)
#plt.axis([-2300000,2100000, -1800000, 1500000])


plt.savefig('output/communities_95_%s_states_nodes_new.jpg' %year)
plt.close()
                

#Take out nodes  
plt.figure(figsize = (15,11))
m = bm.Basemap(width = width, height = height, projection = 'aea', resolution = 'l', lat_1 = 29.5, lat_2 = 45.5, lat_0 = 38.5, lon_0 = -97)
m.drawcountries()
m.drawcoastlines()
m.drawstates()
plt.show()    

nx.draw_networkx_edges(comnetdraw, pos,with_labels = False,alpha = .1, linewidths = 0, 
        #nodelist = list(comsdraw.sort(['pop']).index),
        #node_size = sqrt(comsdraw.sort(['pop'])['pop']),
        #node_color = 'gray',
        edgelist = elist)
#plt.axis([-2300000,2100000, -1800000, 1500000])


plt.savefig('output/communities_95_%s_states_new.jpg' %year)
plt.close()
                
                
#Squared
elist_all = zip(zip(*comcol.index)[0],zip(*comcol.index)[1])
#[(u,v) for (u,v,d) in comnet.edges(data = True)]
ecol = comcol['cnt']**2
#.apply(^2, axis = 1
#[d['weight'] for (u,v,d) in comnet.edges(data = True)]

#Plot with weights that depend on number of overlapping communities
netplot_edges('output/communities_10_squared_100_%s_new.jpg' %year,width, height, comnetdraw,pos,with_labels = False,alpha = 0.1, linewidths = 0, 

        edgelist = elist_all,
        edge_color = ecol,
        edge_cmap = pl.cm.Greys
        )   
 

# Linear
ecol = comcol['cnt']
#.apply(^2, axis = 1
#[d['weight'] for (u,v,d) in comnet.edges(data = True)]

#Plot with weights that depend on number of overlapping communities
netplot_edges('output/communities_10_lin_100_%s_new.jpg' %year,width, height, comnetdraw,pos,with_labels = False,alpha = 0.1, linewidths = 0, 
        edgelist = elist_all,
        edge_color = ecol,
        edge_cmap = pl.cm.Greys
        )   
  
#nx.draw(mgdraw, pos,with_labels = False,alpha = .7, linewidths = 0.5, width = 0)

#output network

comcol.to_csv('output/comcol_new.csv')

##Formalize
#Do one where you weight degree by (100 - number of times in the same community) / 100.
#Both weighted sum and weighted average - most diverse places and biggest hugs


#Then try to pick one set of communities
#The best one is picked in 6 of the 10 times I try running it. That's saved as 'output/comsformal.csv'

for i in [23]:    
    p2 = cm.best_partition(comnet)
    comsdraw2 = dict2column(comsdraw, p2,'formalcom')
    coms2 = dict2column(coms, p2,'formalcom')

    netplot('output/test2comdetect%s_new.jpg' %i,width, height,mgdraw,pos,with_labels = False,alpha = 1, linewidths = 0.5, width = 0,
        nodelist = list(comsdraw2.sort(['pop']).index),
        node_size = sqrt(comsdraw2.sort(['pop'])['pop']),
        node_color = comsdraw2.sort(['pop'])['formalcom'])
       
      #  coms2.to_csv('output/comsformal.csv')
