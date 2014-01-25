"""
Export plots of networks easily 
"""
import matplotlib.pyplot as plt
import networkx as nx

def netplot(path, graph, posdict, **args):
    

    plt.figure(figsize = (8,4))
    nx.draw(graph, pos = posdict, **args)
    plt.xlim = (-165,-65)
    plt.ylim = (15,65)

    plt.savefig(path)


