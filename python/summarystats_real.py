#New version of summary stats
#Have to construct from m2m since otherwise we get too many local moves


import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#import pyproj
import numpy as np
from scipy.stats import gaussian_kde

os.chdir("/Users/Eyota/projects/thesis")

#Bring in metros
metros = pd.io.parsers.read_csv("output/msadata.csv")
metros = metros.set_index('id')

prlist = [10260, 46580, 10380, 25020, 32420, 41900, 41980, 17620, 42180, 21940, 27580, 49500, 38660]
metros = metros.drop(prlist)
links = pd.DataFrame()
#Bring in and total ins and outs for all years
for yr in ['0405','0506','0607','0708','0809','0910']:

    m2m = pd.io.parsers.read_csv('output/m2m%s.csv' %yr)

    m2m.columns = ['source','target','e_%s' %yr,'r_%s' %yr,'agi_%s' %yr]
    
    if yr == '0405':
        links = m2m.fillna(-99) #Flag negative/NA AGIs so they don't get incorporated into the links later. Pandas automatically drops NaNs in sum for the appropriate columns
    else:
        links = pd.merge(links, m2m.fillna(-99), how = 'outer', left_on = ['source','target'], right_on = ['source','target'])
    inm = m2m.groupby('target')
    inm = inm.agg(np.sum)
    inm = inm.drop('source', axis = 1)
    inm.columns = ['e_in_%s' %yr, 'r_in_%s' %yr, 'agi_in_%s' %yr]
    outm = m2m.groupby('source')
    outm = outm.agg(np.sum)
    outm = outm.drop('target', axis = 1)
    outm.columns = ['e_out_%s' %yr, 'r_out_%s' %yr, 'agi_out_%s' %yr]
    metros = pd.merge(metros,inm, how = 'left', left_index = True, right_index = True)
    metros = pd.merge(metros,outm, how = 'left', left_index = True, right_index = True)

print metros.sort('e_in_0910', ascending = False)[['MSAName','e_in_0910','r_in_0910','agi_in_0910']].iloc[0:20]
print metros.sort('e_out_0910', ascending = False)[['MSAName','e_out_0910']].iloc[0:20]


print metros.sort('e_in_0910', ascending = False)[['MSAName','e_in_0910','r_in_0910','agi_in_0910']].iloc[0:20]

#output

#Missing data are all 0 migrants
links.fillna(0, inplace = True)
#Turn the missing AGIs in links back into NaNs
#Only AGI variables have values of -99
(links == -99).sum()
links = links.replace(-99, NaN)

metros.to_csv('output/metrototals.csv')
links.to_csv('output/m2m_allyrs.csv')


lcolnames = list(links.columns)
linklab = pd.merge(links, metros[['MSACode','MSAName']], how = 'left', left_on = 'source', right_on = 'MSACode')
linklab = pd.merge(linklab, metros[['MSACode','MSAName']], how = 'left', left_on = 'target', right_on = 'MSACode')
linklab.columns = lcolnames +['s_fips','s_name','t_fips','t_name']

#look at high per capita links
yr = '0910'
#Giving me way more nulls here than it should. ~~ 9500 where the denominator != 0 but still returning Nan
linklab['percap_0910'] = (1.0 * links['agi_0910'] )/(1.0 *links['e_0910'])
linklab['percap_0910'] = (1.0 * links['agi_%s' %yr] )/(1.0 *links['e_%s' %yr])
linklab['percap_0910'] = linklab.apply(lambda x: x['agi_%s' % yr] / x['e_%s' %yr], axis = 1)



linklab['percap_0910'] = NaN
linklab[linklab['e_%s' %yr] !=0]['percap_0910'] = linklab[linklab['e_%s' %yr] !=0].apply(lambda x: x['agi_%s' % yr] / x['e_%s' %yr], axis = 1)

print linklab[linklab['e_0910'] > 0].sort('percap_0910', ascending = False)[['e_0910','agi_0910','percap_0910','s_name','t_name']].iloc[0:5]

linklab[(linklab['e_%s' %yr] !=0) & (pd.isnull(linklab['percap_0910']))]


#Total inter-Metro moves by year
for v in ['r','e','agi']:

    nums = totals[['%s_in_0405' %v,'%s_in_0506' %v,'%s_in_0607' %v,'%s_in_0708' %v,'%s_in_0809'%v,'%s_in_0910' %v]]

    plt.figure(figsize = (8,6), dpi = 200)
    plt.plot(range(2004,2010),nums, 'b-o')
    plt.ylabel(v)
    plt.xlabel("Year (Change between April of the year listed and April of the following year)")
    
    # xticks
    locs,labels = plt.xticks()
    plt.xticks(locs, map(lambda x: "%g" % x, locs))
    
    plt.axis([2003,2010,0,max(nums)*1.2])
    plt.subplots_adjust(left = .12, bottom = 0.2)
    #plt.title("%s over time, 2004-2009" %v)
    plt.show()
    plt.savefig('output/summarystats/yrtotals_%s' %v)
    plt.close()

#Metro trends over time
for v in ['r','e','agi']:
    plt.figure(figsize = (8,6), dpi = 200)
    
    for r in metros.iterrows():
        yeardta = r[1][['%s_in_0405' %v,'%s_in_0506' %v,'%s_in_0607' %v,'%s_in_0708' %v,'%s_in_0809'%v,'%s_in_0910' %v]]
        plt.plot(range(2004,2010),yeardta, 'k-' , alpha = .2)
    
    plt.ylabel(v)
    plt.xlabel("Year (Change between April of the year listed and April of the following year)")
    
    # xticks
    locs,labels = plt.xticks()
    plt.xticks(locs, map(lambda x: "%g" % x, locs))  
    plt.savefig('output/summarystats/metrototals_%s_in_lin' %v)    
    plt.yscale('log')
    plt.savefig('output/summarystats/metrototals_%s_out_log' %v)   
    plt.close() 




#Kernel Density Plots
'''
density = gaussian_kde(data)
xs = np.linspace(0,8,200)
density.covariance_factor = lambda : .25
density._compute_covariance()
plt.plot(xs,density(xs))
'''
for v in metros.columns[5:40]:
    plt.figure(figsize = (8,6), dpi = 200)
    density = gaussian_kde(metros[v])
    xs = np.linspace(0,max(metros[v])*1.2)
    plt.plot(xs, density(xs))
    plt.xlabel(v)
    plt.savefig('output/summarystats/densities/mdens_%s_lin' %v)
    plt.yscale('log')
    plt.savefig('output/summarystats/densities/mdens_%s_log' %v)
    plt.close()
   
    #per capita
    dpop = gaussian_kde((1.0*metros[v]) / metros['pop'])
    xs = np.linspace(0,max((1.0*metros[v])/metros['pop'])*1.2)
    plt.plot(xs, dpop(xs))
    plt.xlabel('%s per capita' %v)
    plt.savefig('output/summarystats/densities/mdens_%s_percapita' %v)
    plt.close()


#Look at scatter plot of exemptions vs per capita income
for yr in ['0405','0506','0607','0708','0809','0910']:
    plt.plot(metros['e_in_%s' %yr],(1.0 * metros['agi_in_%s' %yr] )/metros['e_in_%s' %yr], 'bo') 
    plt.xscale('log')
    plt.xlabel('Exemptions')
    plt.ylabel('Per Capita AGI')
    plt.savefig('output/summarystats/amtvsinc_metros_%s' %yr)
    plt.close()
    
    plt.plot(links['e_%s' %yr],(1.0 * links['agi_%s' %yr] )/links['e_%s' %yr], 'bo', alpha = .05) 
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Exemptions')
    plt.ylabel('Per Capita AGI')
    plt.savefig('output/summarystats/amtvsinc_links_%s' %yr)
    plt.close()