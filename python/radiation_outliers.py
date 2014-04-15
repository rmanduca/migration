#Program to compare radiation model predictions to actual movement, for 2010 for now.
#Looking at flows from MSAs to both counties and MSAs
#Makes lists of the top 20 flows predicted,

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
    
predval.to_csv('output/predval_0910.csv')

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

m2m['sst'] = (m2m['e_0910'] - m2m['e_0910'].mean())**2
m2m['ssr'] = m2m['resid'] ** 2
sst = m2m['sst'].sum()
ssr = m2m['ssr'].sum()
1-ssr/sst
#Pretty bad R2 = 0.15 or so

#Note that radiation model predicts less migration than observed between MSAs. 
#I think this must have to do with the fact that we include MSA-county flows in figuring out the proportions but not later on
#Actually maybe not - the proportions were weighted based on total flows, so the above should be accounted for
#So maybe the radiation model predicts more closer moves/more msa-county moves than we see?

totflows.sum() #5958857 all migration in the country
flows.groupby(['cnty_dest','cnty_orig']).agg(sum) #Break out by origin and dest msa/county
#5280236 MSA to MSA, 
#285267 MSA to cnty, total 5565503 from msas
#301621 cnty to msa
#91733 cnty to cnty. Sums to 5958857


m2m['e_0910'].sum() # 5280236
m2m['pred'].sum() #4731881

#Check out cnty/noncnty flows
predval.loc[msas].sum().sum() #5510155 from msas. This is only 99% of the total flows. Should be the same since we're using those to scale?
predval.loc[msas,prlist].sum().sum() #And that includes 978 predicted from PR

radmo.loc[msas].sum().sum() #9410673157. 99.9% of 9420000000, so it's not just misc numbers getting lost

#Check out where things are getting lost
check = totflows.loc[msas]
check['id'] = check.index
check['pred'] = check.apply(lambda x: predval.loc[x['id']].sum() , 1)
check['ratio'] = check['pred'] / check['Exmpt_Num']
check['resid'] = check['Exmpt_Num'] - check['pred'] 
check.sort('resid', ascending = False).iloc[0:5][['resid']]

#These are all the big MSAs - NYC, LA, Chicago, Dallas, DC, Miami, Houston, Riverside
top10 = check.sort('resid', ascending = False).iloc[0:10].index
radmo.loc[top10].sum().sum() / (10*10000000) # 97.5 percent
radmo.loc[top10].apply(sum, 1) #93% for NY, shrinks from there

#So the radiation model is especially prone to undercounting in really big MSAs. This accounts for the missing 1% of migrants
#Would like to know better why this is... 
#Maybe has to do with a transition to int and rounding down somewhere?

#Back to checking pct from counties
predval.loc[msas,msas].sum().sum() #4908460. That's somewhat bigger than 47, so there are about 176,579 migrants predicted flowing between MSAs that actually don't have flow.







#Add in short names and populations and distances
msadata = pd.io.parsers.read_csv('output/msadata_shortname.csv')
msadata['id'] = msadata['id'].apply(str)
msadata.set_index('id',inplace = True)
shortnames = msadata[['shortname','pop']]

m2m = pd.merge(m2m, shortnames, left_on = 'source', right_index = True)
m2m = pd.merge(m2m, shortnames, left_on = 'target', right_index = True,suffixes = ['_s','_t'])



#Check out top 20
m2m.sort('e_0910',ascending = False)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/top_actual.csv')
m2m.sort('pred',ascending = False)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/top_pred.csv')
m2m.sort('resid',ascending = False)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/pos_resid.csv')
m2m.sort('resid',ascending = True)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/neg_resid.csv')
m2m.sort('pct',ascending = False)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/neg_pct.csv')
m2m.sort('pct',ascending = True)[['shortname_s','shortname_t','pred','e_0910','pop_s','pop_t','dist']].iloc[0:30].to_csv('output/radiation/pos_pct.csv')


#Plot predicted vs actual
plt.figure()
plt.plot(m2m['e_0910'],m2m['pred'], 'bo')
plt.savefig('output/radiation/rad_predvsactual.pdf')
plt.close()


#Plot residuals vs pop product (?)
m2m['popprod'] = m2m['pop_s']*m2m['pop_t']
m2m['pplog'] = m2m['popprod'].apply(log10)
m2m['ppgroup'] = m2m['pplog'].apply(ceil)

#Check out number of cases
m2m[['ppgroup','e_0910']].groupby('ppgroup').agg(len)

boxes = []
for i in range(9,16):
    boxes.append(m2m[m2m['ppgroup']==i]['resid'])

plt.figure()
plt.boxplot(boxes,0,'')
plt.xticks(range(8),["",'10^9','10^10','10^11','10^12','10^13','10^14','10^15'])
plt.savefig('output/radiation/rad_resid_popprod.pdf')
plt.close()


#Plot residuals vs distance
#250km boxes up to 3000
m2m['dgroup'] = m2m['dist'].apply(lambda x: ceil(x / 250)*250)
m2m['dgroup'] = m2m['dgroup'].where(m2m['dgroup'] <=3000,3000)

boxes = []
for i in range(250,3250,250):
    boxes.append(m2m[m2m['dgroup']==i]['resid'])

plt.figure()
plt.boxplot(boxes,0,'')
plt.xticks(range(13),range(0,3250,250))
plt.savefig('output/radiation/rad_resid_dist.pdf')
plt.close()


#Residuals by source community



#Going to just add predicted values to the flows that had positive amounts. This will drop flows that 
#actually registered zeros, so it will bias the results somewhat. But I'm hoping that the flows with 
#material predicted values will all have at least 
#The mean flo