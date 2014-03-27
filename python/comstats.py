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
         
    
#Degree weighted by % cross-community
wexmpt = mg.degree(weight = 'w_exmpt')
metros = dict2column(metros, wexmpt, 'wexmpt')

#Total degree
deg = mg.degree(weight = 'exmptgross')
metros = dict2column(metros, deg, 'wdeg')

#Average outside com
metros['outcom'] = metros['wexmpt'] / metros['wdeg']

#Degree outside formal community
wform = mg.degree(weight = 'form_exmpt')
metros = dict2column(metros, wform, 'wform')

#avg outside form com
metros['outformcom'] = round(1.0* metros['wform'] / metros['wdeg'],2)

#within comm degree
metros['incom_exmpt'] = metros['wdeg'] - metros['wexmpt']

#Shortnames
metros['shortname'] = metros['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))


metrosdraw = metros.drop(akhi)

#maps
for stat in ['wexmpt','outcom','wdeg', 'wform','outformcom','incom_exmpt','pop']:
    netplot('output/maps_%s.jpeg' %stat,width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(metrosdraw.sort(['pop']).index), 
    node_size = sqrt(metrosdraw.sort(['pop'])['pop']), 
    node_color = metrosdraw.sort(['pop'])[stat],
    alpha = .7, linewidths = 0.5, width = 0)
    
    
netplot('output/maps_%s.jpeg' %'test',width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(metrosdraw[metrosdraw['wexmpt']<100].sort(['pop']).index), 
    node_size = sqrt(metrosdraw[metrosdraw['wexmpt']<100].sort(['pop'])['pop']), 
    node_color = metrosdraw[metrosdraw['wexmpt']<100].sort(['pop'])['wexmpt'],
    alpha = .7, linewidths = 0.5, width = 0)
    
    
netplot('output/maps_%s.jpeg' %'test2',width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(metrosdraw[metrosdraw['wexmpt']>=100].sort(['pop']).index), 
    node_size = sqrt(metrosdraw[metrosdraw['wexmpt']>=100].sort(['pop'])['pop']), 
    node_color = metrosdraw[metrosdraw['wexmpt']>=100].sort(['pop'])['wexmpt'],
    alpha = .7, linewidths = 0.5, width = 0)

#Chicago is dominant
#Lots of places in the midwest have high percentages not in same community, but maybe that's because the communities are less well defined? Try comparing to 
# map just based on if places are in the same community.

#Plots of pop vs degree, weighted vs unweighted, etc

plt.figure()
plt.plot(metros['wdeg'],metros['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/wdegwexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(metros['pop'],metros['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/popwexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(metros['wdeg'],metros['outcom'], 'bo')
#plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/wdegoutcom.jpeg')
plt.close()

plt.figure()
plt.scatter(metros['incom_exmpt'],metros['wexmpt'],c = metros['pop'], s = 100)
#plt.yscale('linear')
#plt.xscale('log')
#plt.axis([0,1000000,0,1000000])
tolabel = metros[ (metros['incom_exmpt']>60000) |( metros['wexmpt'] > 20000)]
#.sort('wexmpt', ascending = False).iloc[0:10]
for label, x, y in zip(tolabel['shortname'],tolabel['incom_exmpt'],tolabel['wexmpt']):
     plt.annotate(
        label, 
        xy = (x, y))
plt.savefig('output/correlations/incom_outcom.jpeg')
plt.close()

#Plot wdeg vs wdeg weighted by outside coms
#Look for within community degree and outside com degree.
#Plot some sort of entropy index based on which communities