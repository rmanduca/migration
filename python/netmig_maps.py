"""
Make maps of metros showing net migration and gross migration
Make plot of links with flows in each direction?
Make plot of inflows vs outflows
"""

import os
import sys
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import random as rd
import pylab as pl
import re
from scipy.stats.stats import pearsonr
from numpy import sqrt, round, abs
#import community as cm

#New Modules
sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from rowtodict import *
from drawnetworks import netplot
from importnetworks import importnetwork
import com2 as cm

os.chdir("/Users/Eyota/projects/thesis")

#Bring in metros
metros = pd.io.parsers.read_csv("output/metrototals.csv")
metros = metros.set_index('id')

metros['shortname'] = metros['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))

metros['netin0910'] = metros['e_in_0910'] - metros['e_out_0910']
metros[['e_in_0910','e_out_0910']].sum()
abs(metros['netin0910']).sum()
#Correlation of in and out gives R2, pct of variation that's just due to reciprocity
#Plot of in vs out in each year

#The above may not be quite right. It's by city not by link. May want to do by link.


plt.figure()
plt.scatter(metros['e_in_0910'],metros['e_out_0910'])
plt.xscale('log')
plt.yscale('log')
plt.savefig('output/correlations/in_vs_out.jpeg')
plt.close()
pearsonr(metros['e_in_0910'],metros['e_out_0910'])
#Map of net in
#Map of net in divided by total migrants
#Map of total flows in and out