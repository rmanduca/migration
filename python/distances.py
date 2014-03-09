'''
Program to calculate distances between all MSAs and counties, and then to run 
gravity and radiation models on them

'''
import os
import sys
import pandas as pd
#from scipy.spatial.distance import pdist
import pyproj

sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from distance import great_circle_distance

os.chdir("/Users/Eyota/projects/thesis")

cmsas = pd.io.parsers.read_csv('output/cmdata.csv')
cmsas['fips2'] = cmsas['id']
cmsas.set_index('id', inplace = True)

msalist= cmsas[pd.isnull(cmsas['fips'])].index
dists = pd.DataFrame(index = cmsas.index, columns = cmsas.index)

for c in dists.columns:
    origin = (cmsas.loc[c]['lat'],cmsas.loc[c]['lon'])
    dists[c] = cmsas.apply(lambda x: great_circle_distance(origin, (x['lat'],x['lon'])) , axis = 1)
    
dists.to_csv('output/distance_matrix.csv')    
msadists = dists.loc[msalist,msalist]
msadists.to_csv('output/distance_matrix_msas.csv')


#Radiation Model
rad = pd.DataFrame(index = cmsas.index, columns = cmsas.index)

def popcirc(x,y):
    cutoff = dists.loc[x,y]
    quallist = dists[dists[x] < cutoff].index
    totpop = cmsas.loc[quallist].sum()['pop']
    return totpop
    
def radiation(x,y):
    #Gives radiation predicted fraction from x to y
    xpop = cmsas.loc[x]['pop']
    ypop = cmsas.loc[y]['pop']
    circpop = popcirc(x,y)
    rad = (xpop*ypop)/((xpop + circpop)*(xpop+ypop+circpop))
    return rad

#In the radiation matrix, note that the x,yth cell is the flow from x to y
for c in rad.columns[67:]:
    print c
    rad[c] = cmsas.apply(lambda x: radiation(x['fips2'],c), axis = 1)
        
rad.to_csv('output/radiation_matrix.csv')