import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import random as rd
import pylab as pl
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

#Import 0910 data
metros, mg, nodedata = importnetwork(year)

#Community weights from before
comweights = pd.io.parsers.read_csv('output/comcol.csv')
comweights.set_index(['0','1'], inplace = True)

#formal communities based on redoing com detection on 100-runs
comsform = pd.io.parsers.read_csv('output/comsformal.csv')
comsform.set_index('id',inplace = True)
comsform = comsform[['pop','lat','lon','MSAName','formalcom']]

#Draw setup
#Take out AK/HI for now for drawing
akhi = metros[(metros['lon'] > -60) | (metros['lon'] <-125)].index
mgdraw = mg.copy()
mgdraw.remove_nodes_from(akhi)

#Projection
project = pyproj.Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=38.5 +lon_0=-97 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0]+width / 2,t[1] + height / 2)))


#Rescale community weights based on diversity: goes from 0 if always in same community to 1 if always in different ones
comweights['pct_dif'] = (100-comweights['cnt']) / 100.0

for l in mg.edges(data = True):
    try:
        comweights.loc[l[0],l[1]]
    except KeyError:
        weight = 1 
    else:
        weight = comweights.loc[l[0],l[1]]['pct_dif']
    l[2]['w_exmpt'] = round(weight * l[2]['exmptgross'], 2)
    if comsform.loc[l[0],'formalcom'] == comsform.loc[l[1],'formalcom']:
        l[2]['form_exmpt'] = 0
    else:
        l[2]['form_exmpt'] = l[2]['exmptgross']
         
    
wexmpt = mg.degree(weight = 'w_exmpt')
metros = dict2column(metros, wexmpt, 'wexmpt')

#Total degree
deg = mg.degree(weight = 'exmptgross')
metros = dict2column(metros, deg, 'wdeg')

#Average outside com
metros['outcom'] = metros['wexmpt'] / metros['wdeg']

metrosdraw = metros.drop(akhi)

#maps
for stat in ['wexmpt','outcom','wdeg']:
    netplot('output/maps_%s.jpeg' %stat,width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(metrosdraw.sort(['pop']).index), 
    node_size = sqrt(metrosdraw.sort(['pop'])['pop']), 
    node_color = metrosdraw.sort(['pop'])[stat],
    alpha = .7, linewidths = 0.5, width = 0)
    
#Chicago is dominant
#Lots of places in the midwest have high percentages not in same community, but maybe that's because the communities are less well defined? Try comparing to 
# map just based on if places are in the same community.



#Seems like akhi arent working in the com detect right