#Program to compare radiation model predictions to actual movement, for 2010 for now.
#Looking at flows from MSAs to both counties and MSAs
#Makes lists of the top 20 flows predicted,

import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import numpy as np
from scipy.stats import gaussian_kde
from scipy.stats.stats import pearsonr
from scipy.misc import comb
import re
import networkx as nx
import pylab as pl

sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from drawnetworks import netplot
from rowtodict import *
from importnetworks import importnetwork
import com2 as cm


os.chdir("/Users/Eyota/projects/thesis")


#First time import only
'''

#Bring in proportions from the radiaton model. Note that these were all 
#multiplied by 10^8 for ease of storage.
radmo = pd.io.parsers.read_csv('output/radiation_matrix_loop_sdlariv.csv')
radmo['id'] = radmo['id'].apply(str)
radmo.set_index('id', inplace = True)
#Drop PR cities. Leave in flows to them 
prlist = ['10260', '46580', '10380', '25020', '32420', '41900', '41980', '17620', '42180', '21940', '27580', '49500', '38660']
radmo = radmo.drop(prlist)

#Bring in total county-MSA flows for 2009-2010 to scale properly
flows = pd.io.parsers.read_csv('output/c2m0910.csv')
#Check out MSA-county and MSA-MSA flows
flows['cnty_orig'] = flows.apply(lambda x: x['source'][0] == 'c',1)
flows['cnty_dest'] = flows.apply(lambda x: x['target'][0] == 'c',1)

#Aggregate by source
totflows = flows.groupby('source')
totflows = totflows.agg(np.sum)

#Rescale radiation model predictions by total number of outmigrants
predval = radmo
msas = [x for x in predval.index if x[0] != 'c']
for i in msas:
    print i
    predval.loc[i] = radmo.loc[i].apply(lambda x: x / 10000000 * totflows.loc[i,'Exmpt_Num'])
    
predval[msas].to_csv('output/predval_0910_sdlariv.csv')
'''
predval = pd.io.parsers.read_csv('output/predval_0910_sdlariv.csv')
predval['id'] = predval['id'].apply(str)
predval.set_index('id',inplace= True)

#Bring in m2m_allyears 
m2m = pd.io.parsers.read_csv('output/m2m_allyrs.csv')
m2m['source'] = m2m['source'].apply(int).apply(str)
m2m['target'] = m2m['target'].apply(int).apply(str)

#Bring in distances
dists = pd.io.parsers.read_csv('output/distance_matrix.csv')
dists['id'] = dists['id'].apply(str)
dists.set_index('id', inplace = True)

pred = []
confirm = []
distlist = []
for i in m2m.iterrows():
    print i[0]
    pred.append(round(predval.loc[i[1]['source'],i[1]['target']],2))
    confirm.append(i[1]['e_0910'])
    distlist.append(round(dists.loc[i[1]['source'],i[1]['target']],2)/1000)
    
m2m['dist'] = distlist

m2m['pred'] = pred
m2m['resid'] = m2m['e_0910'] - m2m['pred']
m2m['pct'] = m2m['resid'] / m2m['e_0910']


m2m['min'] = m2m[['e_0910','pred']].apply(min,axis = 1)

#Compute common part stat
commonpart = 2.0*m2m['min'].sum() / (m2m['e_0910'].sum() + m2m['pred'].sum())
commonpart #0.533

#Add in short names and populations and distances
msadata = pd.io.parsers.read_csv('output/msadata_shortname.csv')
msadata['id'] = msadata['id'].apply(str)
msadata.set_index('id',inplace = True)
shortnames = msadata[['shortname','pop']]

m2m = pd.merge(m2m, shortnames, left_on = 'source', right_index = True)
m2m = pd.merge(m2m, shortnames, left_on = 'target', right_index = True,suffixes = ['_s','_t'])

m2m.sort('resid',ascending = False)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/pos_resid_lasdriv.csv')
m2m.sort('resid',ascending = True)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/neg_resid_lasdriv.csv')

#Distance classes
m2m['dgroup'] = m2m['dist'].apply(lambda x: ceil(x / 250)*250)
m2m['dgroup'] = m2m['dgroup'].where(m2m['dgroup'] <=3000,3000)

#### Try to do stat sig for distance outliers? ####
def diststat(df, dis, res):
    dat = df[(df['dgroup'] == dis) & (abs(df['resid']) >= res)]
    tot = dat.shape[0]
    posi = dat[dat['resid'] > 0].shape[0]
    
    prob = 0.0
    
    for i in range(posi, tot+1):
        print prob
        prob += comb(i,tot) * 1/2**tot
        
    return [tot,posi,prob]
    #Normal approx to binomial
    #Get prob of higher 
    #Return prob




######Prep for maps#######
year = '0910'
width = 4700000
height = 3100000

#Import 0910 data
metros, mg, nodedata = importnetwork(year)

#String FIPS code
metros['id'] = metros['MSACode'].apply(str)

#Draw setup
#Take out AK/HI for now for drawing
akhi = metros[(metros['lon'] > -60) | (metros['lon'] <-125)].index
mgdraw = mg.copy()
mgdraw.remove_nodes_from(akhi)

#Projection
project = pyproj.Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=38.5 +lon_0=-97 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
t = project(metros['lon'],metros['lat'])
pos = dict(zip(metros.index,zip(t[0]+width / 2,t[1] + height / 2)))

#colormap = cm = plt.get_cmap('Spectral') 
#######Done with prep########

#Maps of total residuals by metro
sresid = m2m[['source','resid']].groupby('source').agg('sum').sort('resid',ascending = False)
tresid = m2m[['target','resid']].groupby('target').agg('sum').sort('resid',ascending = False)
sres = pd.merge(sresid, metros, left_index = True, right_on = 'id')
tres = pd.merge(tresid, metros, left_index = True, right_on = 'id')
'''
netplot('output/radiation/metro_s_resid.jpeg',width, height, mgdraw, pos, with_labels = False, 
    nodelist = list(sres.sort('pop').index), 
    node_size = sqrt(sres.sort(['pop'])['pop']), 
    node_color = sres.sort(['pop'])['resid'],cmap = colormap,
    alpha = .7, linewidths = 0.5, width = 0)
   ''' 
netplot('output/radiation/metro_t_resid_sdlariv.jpeg',width, height, mgdraw, pos, with_labels = False, 
    nodelist = list(tres.sort('pop').index), 
    node_size = sqrt(tres.sort(['pop'])['pop']), 
    node_color = tres.sort(['pop'])['resid'],
    alpha = .7, linewidths = 0.5, width = 0)
    
tres.to_csv('output/radiation/metro_t_resid_lasdriv.csv')
tres.iloc[0:30].to_csv('output/radiation/metro_t_pos_resid_lasdriv.csv')
tres.sort('resid').iloc[0:30].to_csv('output/radiation/metro_t_neg_resid_lasdriv.csv')

##Maps of large long-distance flows
biglong = m2m[(m2m['resid'].abs() >500) & (m2m['dist'] >500)].sort('e_0910')

biglong[['shortname_s','shortname_t','e_0910','pred','resid','dist']].sort('resid',ascending = False).to_csv('output/radiation/biglong.csv')
elist = zip(biglong['source'].apply(int),biglong['target'].apply(int))

ecol = biglong['e_0910']

nlist = biglong['source'].append(biglong['target']).apply(int).unique()
nsize = metros.loc[nlist]['pop']

netplot('output/radiation/biglong_core.pdf',width, height, mgdraw,pos,with_labels = False,alpha =.8,width = 3, 
        nodelist = list(nlist),
        node_size = (sqrt(nsize))*0.1,
        node_color = 'black',
        edgelist = elist,
        edge_color = ((ecol**.75)),
        edge_cmap = pl.cm.Greys,
        edge_vmin = 0
        )   
        
#Map of all flows
msort = m2m.sort('e_0910')
elist = zip(msort['source'].apply(int),msort['target'].apply(int))

ecol = msort['e_0910']

nlist = msort['source'].append(msort['target']).apply(int).unique()
nsize = metros.loc[nlist]['pop']

netplot('output/radiation/allflows.jpg',width, height, mgdraw,pos,with_labels = False,alpha =.8,width = 1, 
        nodelist = list(nlist),
        node_size = (sqrt(nsize))*0.1,
        node_color = 'black',
        edgelist = elist,
        edge_color = ((ecol**.3)),
        edge_cmap = pl.cm.Greys,
        edge_vmin = 0
        )   