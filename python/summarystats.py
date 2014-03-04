#Summary Statistics on Total migration flows

import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pyproj

os.chdir("/Users/Eyota/projects/thesis")

#Bring in metros
metros = pd.io.parsers.read_csv("output/msadata.csv")
metros = metros.set_index('id')


#Yearly totals 
yrtotals = pd.io.parsers.read_csv('output/yrtotals.csv')
yrtotals['year'] = 2004 + yrtotals.index
yrtotals = yrtotals.set_index('year')

for v in ['Return_Num','Exmpt_Num','Aggr_AGI']:
    plt.figure(figsize = (8,6), dpi = 200)
    plt.plot(yrtotals.index,yrtotals[v], 'b-o')
    plt.ylabel(v)
    plt.xlabel("Year (Change between April of the year listed and April of the following year)")
    
    # xticks
    locs,labels = plt.xticks()
    plt.xticks(locs, map(lambda x: "%g" % x, locs))
    
    plt.axis([2003,2010,0,max(yrtotals[v])*1.2])
    plt.subplots_adjust(left = .12, bottom = 0.2)
    #plt.title("%s over time, 2004-2009" %v)
    plt.show()
    plt.savefig('output/summarystats/yrtotals_%s' %v)
    plt.close()
    
#MSA Totals over time
msatots = pd.io.parsers.read_csv('output/msatotals.csv')
msatots = msatots.set_index('msa')

#Remove PR
prlist = [10260, 46580, 10380, 25020, 32420, 41900, 41980, 17620, 42180, 21940, 27580, 49500, 38660]
msatots = msatots.drop(prlist)

#add changes
msatots['change'] = 
    
for v in ['r','e','agi']:
    plt.figure(figsize = (8,6), dpi = 200)
    msatots['change_%s' %v] = msatots[ '%s_in_0910'%v] - msatots[ '%s_in_0405'%v] 
    
    for r in msatots.iterrows():
        yeardta = r[1][['%s_in_0405' %v,'%s_in_0506' %v,'%s_in_0607' %v,'%s_in_0708' %v,'%s_in_0809'%v,'%s_in_0910' %v]]
        plt.plot(range(2004,2010),yeardta, 'k-' , alpha = .1)
        
    plt.yscale('log')

        
