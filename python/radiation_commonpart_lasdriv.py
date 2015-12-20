'''
Computing the Common Part Index, based on the Sorensen Index

'''

import os
import sys
#import networkx as nx
import pandas as pd
#import matplotlib.pyplot as plt
#import pyproj
import numpy as np
#from scipy.stats import gaussian_kde
#from scipy.stats.stats import pearsonr
import re
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from drawnetworks import netplot


os.chdir("/Users/Eyota/projects/thesis")


predval = pd.io.parsers.read_csv('output/predval_0910.csv')
predval.set_index('id',inplace = True)

#Bring in m2m_allyears 
m2m = pd.io.parsers.read_csv('output/m2m_allyrs.csv')
m2m['source'] = m2m['source'].apply(int).apply(str)
m2m['target'] = m2m['target'].apply(int).apply(str)


#Match predictions and Observed
pred = []
confirm = []
for i in m2m.iterrows():
    print i[0]
    pred.append(round(predval.loc[i[1]['source'],i[1]['target']],2))
    confirm.append(i[1]['e_0910'])
    
m2m['pred'] = pred
m2m['confirm'] = confirm

assert m2m.apply(lambda x:  x['confirm'] == x['e_0910'],axis = 1).sum() == m2m.shape[0]

#Compute minimum of predicted and observed

m2m['min'] = m2m[['e_0910','pred']].apply(min,axis = 1)

commonpart = 2.0*m2m['min'].sum() / (m2m['e_0910'].sum() + m2m['pred'].sum())
commonpart #0.52668