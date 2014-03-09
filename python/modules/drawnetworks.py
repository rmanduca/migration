"""
Export plots of networks easily 
"""
import matplotlib.pyplot as plt
import networkx as nx
import mpl_toolkits.basemap as bm


def netplot(path, w, h, graph, posdict, **args):
    plt.figure(figsize = (15,11))
    m = bm.Basemap(width = w, height = h, projection = 'aea', resolution = 'l', lat_1 = 29.5, lat_2 = 45.5, lat_0 = 38.5, lon_0 = -97)
    m.drawcountries()
    m.drawcoastlines()
    plt.show()    

    nx.draw(graph, pos = posdict, **args)
    #plt.axis([-2300000,2100000, -1800000, 1500000])


    plt.savefig(path)
    plt.close()


