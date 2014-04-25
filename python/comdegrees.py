'''
Program to 
--Calculate degree of each node within each other community

'''


import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import random as rd
import pylab as pl
import re

from numpy import sqrt, round
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

#Import 0910 data
metros, mg, nodedata = importnetwork(year)

#Community weights from before
comweights = pd.io.parsers.read_csv('output/comcol.csv')
comweights.set_index(['0','1'], inplace = True)

#formal communities based on redoing com detection on 100-runs
comsform = pd.io.parsers.read_csv('output/comsformal.csv')
comsform.set_index('id',inplace = True)
comsform = comsform[['pop','lat','lon','MSAName','formalcom']]

#Set up blank variables
for i in range(6):
    comsform['com%sdeg' %i] = 0
    
for i in mg.nodes():
    for j in mg[i].keys():
        com = comsform.loc[j,'formalcom']
        comsform.loc[i,'com%sdeg' %com] += mg[i][j]['exmptgross']
        
comsform['wincomdeg'] = comsform.apply(lambda x: x['com%sdeg' % x['formalcom']], axis = 1)