import os
import sys
import pandas as pd
#from scipy.spatial.distance import pdist
import pyproj
from matplotlib.mlab import find

sys.path.append('/Users/Eyota/projects/thesis/code/python/modules')
from distance import great_circle_distance

os.chdir("/Users/Eyota/projects/thesis")

#Distances
dists = pd.io.parsers.read_csv('output/distance_matrix.csv')
dists['id'] = dists['id'].apply(str)
dists.set_index('id', inplace = True)

#County/MSA data
cmsas = pd.io.parsers.read_csv('output/cmdata.csv')
cmsas['fips2'] = cmsas['id']
cmsas.set_index('id', inplace = True)

#Bring in partially completed radiation 
#New
#rad = pd.DataFrame(index = cmsas.index, columns = cmsas.index)
#Bring in existing
rad = pd.io.parsers.read_csv('output/radiation_matrix_loop.csv')
rad['id'] = rad['id'].apply(str)
rad.set_index('id', inplace =True)
startcode = rad['c_72147'][pd.isnull(rad['c_72147'])].index[0]
startrow = find(rad.index == startcode)[0]

def popcirc(x,y):
    cutoff = dists.loc[x,y]
    quallist = dists[dists[x] < cutoff].index # strict inequality prevents y from being included
    totpop = cmsas.loc[quallist].sum()['pop'] - cmsas.loc[x,'pop']
    return totpop
    
def radiation(x,y):
    #Gives radiation predicted fraction from x to y
    #Multiplying by 10 mil to get a ballpark number, then rounding to decrease size (don't want floats)
    xpop = cmsas.loc[x]['pop']
    ypop = cmsas.loc[y]['pop']
    circpop = popcirc(x,y)
    rad = round(10000000.0*(xpop*ypop)/((xpop + circpop)*(xpop+ypop+circpop)))
    return rad
#28020


for i in cmsas.index[startrow:]:
    print i
    for j in cmsas.index:
        if j == i:
            continue
        else:
            rad.loc[i,j] = radiation(i,j)



#In the radiation matrix, note that the x,yth cell is the flow from x to y
for c in rad.columns[startcol:]:
    print c
    rad[c] = test = cmsas.apply(lambda x: radiation(x['fips2'],c), axis = 1)
        
rad.to_csv('output/radiation_matrix_loop.csv')