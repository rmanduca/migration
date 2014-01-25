"""
Start doing statistics!

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

year = '0910'

execfile('code/python/importnetworks.py')

#Play with projections
project = pyproj.Proj('+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')

#pos = dict(zip(metros.index,zip(metros['lon'],metros['lat'])))

t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0],t[1])))

netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

nx.draw(mg, pos = pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)

netplot('output/projectedtest.jpeg', mg, pos, with_labels = False, nodelist = list(metros.index), node_size = metros['pop'] / 50000, alpha = .4, linewidths = 0, width = .1)
