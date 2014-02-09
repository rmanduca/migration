import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import community as cm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot

coms = metros

for i in range(50):
    partition = cm.best_partition(mgdraw)
    coms = dict2column(coms, partition, 'part%s' %i)

size = float(len(set(partition.values())))

count = 0
for com in set(partition.values()) :
    count = count + 1.
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == com]
    nx.draw_networkx_nodes(mgdraw, pos, list_nodes, node_size = 20),
                                node_color = str(count / size))
                                
                                
nx.draw(mgdraw, pos,with_labels = False,alpha = .7, linewidths = 0.5, width = 0)