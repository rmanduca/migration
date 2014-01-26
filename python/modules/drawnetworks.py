"""
Export plots of networks easily 
"""
import matplotlib.pyplot as plt
import networkx as nx

def netplot(path, graph, posdict, **args):
    

    plt.figure(figsize = (15,11))
    nx.draw(graph, pos = posdict, **args)
    plt.axis([-2300000,2100000, -1800000, 1500000])


    plt.savefig(path)


