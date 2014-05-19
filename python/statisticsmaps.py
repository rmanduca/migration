"""
Start doing statistics!
Calculates network statistics on the 09-10 data, and makes maps of them.
Also makes pairwise plots comparing various statistics
"""

import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import mpl_toolkits.basemap as bm
import re
from scipy.stats.stats import pearsonr


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

metros, mg, nodedata = importnetwork(year)

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

stats['shortname'] = stats['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))



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
    netplot('output/netstats/maps_%s_%s.jpeg' %(stat,year),width, height,mgdraw, pos, with_labels = False, 
    nodelist = list(statsdraw.sort(['pop']).index), 
    node_size = sqrt(statsdraw.sort(['pop'])['pop']), 
    node_color = statsdraw.sort(['pop'])[stat],
    alpha = .7, linewidths = 0.5, width = 0)
    
    stats[['shortname','pop',stat]].sort(stat, ascending = False).iloc[0:20].to_csv('output/netstats/top20_%s_%s.csv' %(stat, year))




#Plot statistics vs each other
plt.plot(stats['pop'],stats['wdegree'], 'bo')
plt.xlabel('Population')
plt.ylabel('Weighted Degree')
plt.savefig('output/correlations/pop_wdegree_%s.pdf' %year)
plt.close()
pearsonr(stats['pop'],stats['wdegree'])
plt.plot(stats['degree'],stats['wdegree'], 'bo')
plt.xlabel('Unweighted Degree')
plt.ylabel('Weighted Degree')
'''
tolabel = stats.loc([[ (metros['incom_exmpt']>60000) |( metros['wexmpt'] > 20000)]
#.sort('wexmpt', ascending = False).iloc[0:10]
for label, x, y in zip(tolabel['shortname'],tolabel['incom_exmpt'],tolabel['wexmpt']):
     plt.annotate(
        label, 
        xy = (x, y))
'''
plt.savefig('output/correlations/degree_wdegree_%s.pdf' %year)
plt.close()

plt.plot(stats['degree'],stats['wdegree'], 'bo')
plt.xlabel('Unweighted Degree')
plt.ylabel('Weighted Degree')
plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/degree_wdegree_log_%s.pdf' %year)
plt.close()



plt.plot(stats['pop'],(1.0*stats['wdegree']/stats['pop']), 'bo')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Weighted Degree per Capita')
plt.savefig('output/correlations/pop_migrate_log_%s.pdf' %year)
plt.close()

plt.plot(stats['pop'],stats['wdegree'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Weighted Degree')
plt.savefig('output/correlations/pop_wdegree_log_%s.pdf' %year)
plt.close()
pearsonr(stats['pop'],stats['wdegree']) #0.923

plt.figure()
plt.plot((stats['pop']),stats['flowcloseness'], 'bo')
plt.xlabel('Population')
plt.ylabel('Closeness Centrality')
plt.savefig('output/correlations/pop_flowclose_%s.pdf' %year)
plt.close()
pearsonr(stats['pop'],stats['flowcloseness']) #0.364

plt.figure()
plt.plot((stats['pop']),stats['flowcloseness'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Closeness Centrality')
plt.savefig('output/correlations/pop_flowclose_log_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(stats['pop'],stats['flowbtwnness'], 'bo')
plt.xlabel('Population')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/pop_flowbtwn_%s.pdf' %year)
plt.close()
pearsonr(stats['pop'],stats['flowbtwnness']) #0.863

plt.figure()
plt.plot(stats['pop'],stats['flowbtwnness'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/pop_flowbtwn_log_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(stats[stats['flowbtwnness']>10**(-15)]['pop'],stats[stats['flowbtwnness']>10**(-15)]['flowbtwnness'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/pop_flowbtwn_log_dropoutlier_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(stats['flowcloseness'],stats['flowbtwnness'], 'bo')
plt.xlabel('Closeness Centrality')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/close_btwn_%s.pdf' %year)
plt.close()
pearsonr(stats['flowcloseness'],stats['flowbtwnness']) #0.455


plt.figure()
plt.plot(stats['flowcloseness'],stats['flowbtwnness'], 'bo')
plt.xlabel('Closeness Centrality')
plt.ylabel('Betweenness Centrality')
plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/close_btwn_log_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(stats[stats['flowbtwnness']>10**(-15)]['flowbtwnness'],stats[stats['flowbtwnness']>10**(-15)]['flowcloseness'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.ylabel('Closeness Centrality')
plt.xlabel('Betweenness Centrality')
plt.savefig('output/correlations/close_btwn_log_dropoutlier_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot((stats['wdegree']),(stats['flowbtwnness']), 'bo')
plt.xlabel('Weighted Degree')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/wdeg_btwn_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot((stats['wdegree']),(stats['flowbtwnness']), 'bo')
plt.xlabel('Weighted Degree')
plt.ylabel('Betweenness Centrality')
plt.yscale('log')
plt.xscale('log')
plt.savefig('output/correlations/wdeg_btwn_log_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(stats[stats['flowbtwnness']>10**(-15)]['wdegree'],stats[stats['flowbtwnness']>10**(-15)]['flowbtwnness'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Weighted Degree')
plt.ylabel('Betweenness Centrality')
plt.savefig('output/correlations/wdeg_btwn_log_dropoutlier_%s.pdf' %year)
plt.close()


#Box plots of migrants by pop
#Residuals by source community
labels = ['0-50k','50-100k','100-500k','500k-1 mil','1-5 mil','>5 mil']
bounds = [(0,50000),(50000,100000),(100000,500000),(500000,1000000),(1000000,5000000),(5000000,100000000)]

boxstats = 1.0*stats['wdegree']  /stats['pop']
boxes = [] 
for i in range(6):
    boxes.append(boxstats[(stats['pop'] > bounds[i][0]) & (stats['pop'] <= bounds[i][1])])

plt.figure()
plt.boxplot(boxes,0)
plt.xticks(range(7),['']+labels)
plt.xlabel('Population')
plt.ylabel('Weighted Degree')
plt.savefig('output/netstats/migrate_pop.pdf')
plt.close()

#Do

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
