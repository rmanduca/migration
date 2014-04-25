#Compute modularity for a bunch of different partitions


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
from drawnetworks import netplot
from importnetworks import importnetwork
import com2 as cm

os.chdir("/Users/Eyota/projects/thesis")

year = '0910'
width = 4700000
height = 3100000

metros, mg, nodedata = importnetwork(year)


#formal communities based on redoing com detection on 100-runs
comsform = pd.io.parsers.read_csv('output/comsformal.csv')
comsform.set_index('id',inplace = True)
comsform = comsform[['pop','lat','lon','MSAName','formalcom']]

comsformdict = comsform['formalcom'].to_dict()
print cm.modularity(comsformdict, mg)
