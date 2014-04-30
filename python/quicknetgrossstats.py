#Some statistics on net vs gross flows


import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#import pyproj
import numpy as np
import re

os.chdir("/Users/Eyota/projects/thesis")


grossm = pd.io.parsers.read_csv('output/grossm0910.csv')

grossm['net'] = grossm['exmpt_st'] - grossm['exmpt_ts']
grossm['netabs'] = grossm['net'].apply(abs)
grossm['tot'] = grossm['exmpt_st'] + grossm['exmpt_ts']

grossm['netpct'] = grossm['netabs']*1.0 / grossm['tot']

#Total net percentage
 1.0*grossm['netabs'].sum() / grossm['tot'].sum()  #16 percent
 
 #On average flow
 grossm['netpct'].mean() #44 percent
 
#Excluding zeros
grossm[grossm['exmptgross']>0]['netpct'].mean()  #18 percent
 
#Large flows
grossm[grossm['exmptgross']>1000]['netpct'].mean()  #14 pct over 50, 12 pct over 100, 9 pct over 500 and 1000