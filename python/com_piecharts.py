'''
Program to make pie charts showing the distribution of migrants across formal communities
'''

import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import re
#import matplotlib.colors as colors
#import matplotlib.cm as cmx
#import pyproj
#import mpl_toolkits.basemap as bm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot
import weighted_eigenvector as we
from importnetworks import importnetwork

os.chdir("/Users/Eyota/projects/thesis")

#Bring in formal communities as determined in communitydetect.py
coms = pd.io.parsers.read_csv('output/comsformal.csv')
coms['id'] = coms['id'].apply(str)
coms.set_index('id',inplace = True)
coms['shortname'] = coms['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))

#Bring in MSA-MSA flows
m2m = pd.io.parsers.read_csv('output/m2m0910.csv')
m2m['source'] = m2m['source'].apply(int).apply(str)
m2m['target'] = m2m['target'].apply(int).apply(str)

#Add communities to targets and sources
comsnames = coms[['shortname','formalcom']]

m2m = pd.merge(m2m, comsnames, left_on = 'source', right_index = True)
m2m = pd.merge(m2m, comsnames, left_on = 'target', right_index = True,suffixes = ['_s','_t'])

#Collapse by source
msource = m2m.groupby(['source','formalcom_t']).aggregate(sum)
msource['source'] = zip(*msource.index)[0]
msource['com'] = zip(*msource.index)[1]

totpopcom = coms.groupby('formalcom').agg(sum)

top20 = m2m.groupby('source').agg(sum).sort('Exmpt_Num', ascending = False).iloc[0:20].index
labels = ['Greater Texas','Upper Midwest','East-Central','West','East Coast','Mid-South']
colorslist = ['red','blue','gray','yellow','green','purple']
msalist = range(7) #Taking Atlanta back out+ [11]
fig = plt.figure(figsize = [12.5,6])
for i in range(7):
    ax = fig.add_subplot(2,4,i+1)
    q = msalist[i]
    ax.set_title(comsnames.loc[top20[q],'shortname'])
    piedat = msource[msource['source'] == top20[q]]['Exmpt_Num']
    laborder = zip(*piedat.index)[1]
    labshuf = [labels[j] for j in laborder]
    colorder = [colorslist[j] for j in laborder]
    
    patches, texts = ax.pie(piedat, colors = colorder, labels = labshuf, labeldistance = 1.05)
    for p in range(6):
        texts[p].set_fontsize(7) 
        
ax = fig.add_subplot(2,4,8)
ax.set_title("Total Population")
piedat = totpopcom['pop']
laborder = piedat.index
labshuf = [labels[j] for j in laborder]
colorder = [colorslist[j] for j in laborder]
patches, texts = ax.pie(piedat, colors = colorder, labels = labshuf, labeldistance = 1.05)
for p in range(6):
    texts[p].set_fontsize(7) 
plt.show()
fig.savefig('output/piecharts.pdf')
plt.close()
    