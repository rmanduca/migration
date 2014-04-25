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
comsform = dict2column(comsform, wexmpt, 'wexmpt')

#Total degree
deg = mg.degree(weight = 'exmptgross')
comsform = dict2column(comsform, deg, 'wdeg')

#Average outside com
comsform['outcom'] = comsform['wexmpt'] / comsform['wdeg']

#Degree outside formal community
wform = mg.degree(weight = 'form_exmpt')
comsform = dict2column(comsform, wform, 'wform')

#Current Betweenness
flowbtwnness = nx.current_flow_betweenness_centrality(mg, weight = 'exmptgross')
comsform = dict2column(comsform, flowbtwnness, 'flowbtwnness')

#Current Closeness Centrality 
flowcloseness = nx.current_flow_closeness_centrality(mg, weight = 'exmptgross')
comsform = dict2column(comsform, flowcloseness, 'flowcloseness')

#Degree divided among formal communities
#Set up blank variables
for i in range(6):
    comsform['com%sdeg' %i] = 0
    
#Populate with degree in each community
for i in mg.nodes():
    for j in mg[i].keys():
        com = comsform.loc[j,'formalcom']
        comsform.loc[i,'com%sdeg' %com] += mg[i][j]['exmptgross']
        
comsform['wincomdeg'] = comsform.apply(lambda x: x['com%sdeg' % x['formalcom']], axis = 1)

#Percentage of community's degree going through 
totalcommig = comsform.groupby('formalcom').aggregate(sum)
comsform['commigpct'] = comsform.apply(lambda x: x['com%sdeg' % x['formalcom']] / totalcommig.loc[x['formalcom'],'com%sdeg' %x['formalcom']], axis = 1)

#Com z score from Guimera et al
avgcommig = comsform.groupby('formalcom').aggregate(mean)
stdcommig = comsform.groupby('formalcom').aggregate(std)

comsform['comzscore'] = comsform.apply(lambda x: (x['wincomdeg'] - avgcommig.loc[x['formalcom'],'wincomdeg']) / stdcommig.loc[x['formalcom'],'wincomdeg'], axis = 1)  

#Com participation index from Guimera et al
def particip(x): 
    totsum = 0
    for j in range(6):
       # print totsum
        totsum += (x['com%sdeg' %j]*1.0 / x['wdeg'])**2
    return 1.0- totsum

comsform['partcoef'] = comsform.apply(particip, axis = 1)



#avg outside form com
comsform['outformcom'] = round(1.0* comsform['wform'] / comsform['wdeg'],2)

#within comm degree
comsform['incom_exmpt'] = comsform['wdeg'] - comsform['wexmpt']

#Shortnames
comsform['shortname'] = comsform['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))


metrosdraw = comsform.drop(akhi)

#maps
for stat in ['wexmpt','outcom','wdeg', 'wform','outformcom','incom_exmpt','pop','commigpct','wincomdeg', 'partcoef','comzscore']:
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
plt.plot(comsform['wdeg'],comsform['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Total Weighted Degree')
plt.ylabel('Extra-community Weighted Degree')
plt.savefig('output/correlations/wdegwexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(comsform['pop'],comsform['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Population')
plt.ylabel('Extra-community Weighted Degree')
plt.savefig('output/correlations/popwexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(comsform['flowcloseness'],comsform['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Closeness Centrality')
plt.ylabel('Extra-community Weighted Degree')
plt.savefig('output/correlations/flowclosewexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(comsform['flowbtwnness'],comsform['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Betweenness Centrality')
plt.ylabel('Extra-community Weighted Degree')
plt.savefig('output/correlations/flowbtwnwexmpt.jpeg')
plt.close()

plt.figure()
plt.plot(comsform[comsform['flowbtwnness']>10**(-15)]['flowbtwnness'],comsform[comsform['flowbtwnness']>10**(-15)]['wexmpt'], 'bo')
plt.yscale('log')
plt.xscale('log')
plt.ylabel('Closeness Centrality')
plt.xlabel('Betweenness Centrality')
plt.savefig('output/correlations/close_btwn_log_dropoutlier_%s.pdf' %year)
plt.close()

plt.figure()
plt.plot(comsform['wdeg'],comsform['outcom'], 'bo')
#plt.yscale('log')
plt.xscale('log')
plt.xlabel('Total Weighted Degree')
plt.ylabel('Weighted Degree Outside Formal Community')
plt.savefig('output/correlations/wdegoutcom.jpeg')
plt.close()

plt.figure()
plt.scatter(comsform['incom_exmpt'],comsform['wexmpt'],c = comsform['pop'], s = 100)
#plt.yscale('linear')
#plt.xscale('log')
#plt.axis([0,1000000,0,1000000])
tolabel = comsform[ (comsform['incom_exmpt']>60000) |( comsform['wexmpt'] > 20000)]
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



#Play with fraction of out community migrants going through different places
comsform['outcompct'] = comsform['wexmpt'] / comsform['wexmpt'].sum()
comsform['wdegpct'] = 1.0*comsform['wdeg'] / comsform['wdeg'].sum()
comsform['poppct'] = 1.0*comsform['pop'] / comsform['pop'].sum()

comsform.sort('outcompct', ascending = False)[['shortname','outcompct','wexmpt','wdeg']].iloc[0:10]
comsform.sort('outcompct', ascending = False)[['shortname','outcompct','wexmpt','wdeg']].iloc[0:10].sum()
comsform.sort('wdegpct', ascending = False)[['shortname','wdegpct','wexmpt','wdeg']].iloc[0:10].sum()
comsform.sort('poppct', ascending = False)[['shortname','poppct','wexmpt','wdeg']].iloc[0:10].sum()

plt.figure()
plt.plot(comsform.sort('wdegpct', ascending = False)['wdegpct'], 'r', label = 'All Migrants')
plt.plot(comsform.sort('outcompct', ascending = False)['outcompct'], label = 'Extra-Community Migrants')
plt.plot(comsform.sort('poppct', ascending = False)['poppct'],'y', label = 'Population')
plt.yscale('log')
plt.xlabel('Metro Rank')
plt.ylabel('Percentage of Total')
#Migrants Flowing through Metro')
plt.legend()
plt.savefig('output/correlations/pctmig_outcom.jpeg')
plt.close()
#plt.xscale('log')


#Plots of ranked distributions of within com degree 
plt.figure()
for com in range(6):
    plt.plot(comsform[comsform['formalcom'] == com].sort('commigpct', ascending = False)['commigpct'])

plt.plot(comsform.sort('commigpct', ascending = False)['commigpct'])



#Participation vs Degree

plt.figure()
plt.plot(comsform['partcoef'],comsform['comzscore'], 'bo')
plt.xlabel('Participation Coefficient')
plt.ylabel('Normalized Within-Community Degree')
plt.savefig('output/correlations/particip_wcdeg.jpeg')
plt.close()


#Lists of participation and degree top
comsform.sort('partcoef',ascending = False)[['shortname','com0deg','com1deg','com2deg','com3deg','com4deg','com5deg']].iloc[0:10]



#22pct of all migrants in top 10, 37pct of all inter-com migrants