import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#import pyproj
import numpy as np
import re

os.chdir("/Users/Eyota/projects/thesis")

#Bring in metros
mettot = pd.io.parsers.read_csv("output/metrototals.csv")
mettot = mettot.set_index('id')
mettot['shortname'] = mettot['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))

mettot['netchange'] = mettot['e_in_0910'] - mettot['e_out_0910']
mettot['pctchange'] = 1.0*mettot['netchange'] / mettot['pop']

topmet = mettot.sort('e_in_0910', ascending = False)[['shortname','pop','e_in_0910','e_out_0910','netchange']].iloc[0:20]
for var in ['pop','e_in_0910','e_out_0910','netchange']:
    topmet[var] = topmet[var].apply(lambda x: "{:,}".format(int(round(x))))
topmet.columns = ['MSA','Population','In-migrants','Out-migrants','Net Migration']
latex = file('output/tables/top_10_metros_in.tex', 'w')
latex.write(topmet.iloc[0:10].to_latex(index = False).replace('lllll','lrrrr')
)
latex.close()

toppct = mettot.sort('pctchange', ascending = False)[['shortname','pop','e_in_0910','e_out_0910','netchange','pctchange']].iloc[0:20]
toppct_big = mettot[mettot['pop'] > 100000].sort('pctchange', ascending = False)[['shortname','pop','e_in_0910','e_out_0910','netchange','pctchange']].iloc[0:20]


mettot.sort('netchange', ascending = False)[['shortname','netchange']].iloc[0:10]

mettot.sort('netchange')[['shortname','netchange']].iloc[0:10]

mettot['gross'] = mettot['e_in_0910'] + mettot['e_out_0910']
mettot['absnet'] = mettot['netchange'].apply(abs)

1.0*mettot['absnet'].sum() / mettot['gross'].sum()   #7.1 percent


#In and out mig rate
mettot['inrate'] = 1.0* mettot['e_in_0910'] / mettot['pop']

mettot.sort('inrate', ascending = False)[['shortname','pop','e_in_0910','e_out_0910','netchange','inrate']].iloc[0:20]

