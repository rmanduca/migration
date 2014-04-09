#Program to compare radiation model predictions to actual movement, for 2010 for now.
#Looking at flows from MSAs to both counties and MSAs

import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#import pyproj
import numpy as np
from scipy.stats import gaussian_kde
import re

os.chdir("/Users/Eyota/projects/thesis")

#Bring in proportions from the radiaton model. Note that these were all 
#multiplied by 10^8 for ease of storage.

radmo = pd.io.parsers.read_csv('output/radiation_matrix_loop.csv')
radmo['id'] = radmo['id'].apply(str)
radmo.set_index('id', inplace = True)
#Drop PR cities. Leave in flows to them 
prlist = ['10260', '46580', '10380', '25020', '32420', '41900', '41980', '17620', '42180', '21940', '27580', '49500', '38660']
radmo = radmo.drop(prlist)

flows = pd.io.parsers.read_csv('output/c2m0910.csv')

totflows = flows.groupby('source')
totflows = totflows.agg(np.sum)

predval = radmo
msas = [x for x in predval.index if x[0] != 'c']
for i in msas:
    print i
    predval.loc[i] = radmo.loc[i].apply(lambda x: x / 10000000 * totflows.loc[i,'Exmpt_Num'])
    

#Bring in m2m_allyears 
m2m = pd.io.parsers.read_csv('output/m2m_allyrs.csv')
m2m['source'] = m2m['source'].apply(int).apply(str)
m2m['target'] = m2m['target'].apply(int).apply(str)


pred = []
confirm = []
for i in m2m.iterrows():
    print i[0]
    pred.append(round(predval.loc[i[1]['source'],i[1]['target']],2))
    confirm.append(i[1]['e_0910'])
m2m['pred'] = pred
m2m['resid'] = m2m['e_0910'] - m2m['pred']
m2m['pct'] = m2m['resid'] / m2m['e_0910']

m2m['sst'] = (m2m['e_0910'] - m2m['e_0910'].mean())**2
m2m['ssr'] = m2m['resid'] ** 2
sst = m2m['sst'].sum()
ssr = m2m['ssr'].sum()
1-ssr/sst
#Pretty bad R2 :-(



#Plot predicted vs actual
plt.figure()
plt.plot(m2m['e_0910'],m2m['pred'], 'bo')
plt.savefig('output/radiation_predvsactual.jpeg')
plt.close()



#Going to just add predicted values to the flows that had positive amounts. This will drop flows that 
#actually registered zeros, so it will bias the results somewhat. But I'm hoping that the flows with 
#material predicted values will all have at least 
#The mean flo