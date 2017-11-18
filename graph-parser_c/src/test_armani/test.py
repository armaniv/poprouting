import networkx as nx
from netdiff import NetJsonParser
from netdiff.utils import _netjson_networkgraph as to_netjson
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import collections as col

import warnings
warnings.filterwarnings("ignore")



def ReadGrafoDaJson(url):
    netJSON = NetJsonParser(file=url)
    grafo = netJSON.graph
    return grafo



def PrintGrafoInJson(G,njproto='OLSR',njversion='0.1',njrevision='a09z',njmetric='ETX'):
    js= to_netjson(njproto,
                    njversion,
                    njrevision,
                    njmetric,
                    G.nodes(data=True),
                    G.edges(data=True), dict=True)
    f1=open('./topology.json', 'w+')
    f1.write(json.dumps(js, indent=4))
    f1.close()



def GeneraGrafoCaveman(num,size,randWeight=False):
    G = nx.connected_caveman_graph(num, size)
    for u,v,d in G.edges(data=True):
        if(randWeight==False):
            d['weight']=1
        else:
            d['weight']=np.random.uniform(1.0,1.1)
    return G



#   p=b*exp(-d/aL)
def GeneraGrafoWaxman(num,b=0.4,a=0.1,randWeight=False):
    G = nx.waxman_graph(num,beta=b,alpha=a)
    for u,v,d in G.edges(data=True):
        if(randWeight==False):
            d['weight']=1
        else:
            d['weight']=np.random.uniform(1.0,1.1)
    return G



def  BrandesCutPoint(g):
    #per compatibilita' con libreria C, rimuvo eventali nodi sconnessi 
    g.remove_nodes_from(nx.isolates(g))
    
    n_nodes = len(g.nodes())
    ap = [x for x in nx.articulation_points(g)]
    bconn = list(nx.biconnected_component_subgraphs(g))

    cp_dict = {}

    for p in ap:
        cp_dict[p] = [b for b in bconn if p in b]

    bc = col.defaultdict(int)
    
    for p, bconns in cp_dict.items():
        for bcs in bconns:
            h=nx.Graph(g)
            for altrebcs in bconns:
                if(altrebcs!=bcs):
                    rimuovi = altrebcs.nodes()
                    rimuovi.remove(p)
                    h.remove_nodes_from(rimuovi)
            b = nx.betweenness_centrality(h, weight='weight',endpoints=False,normalized=False)[p]
            bc[p] += b
        bc[p] += (n_nodes - 1)
    for n, b in nx.betweenness_centrality(g, weight='weight',endpoints=True,normalized=False).iteritems():
        if n not in ap:
            bc[n] = b
    return bc



def PrintDizionarioToCsv(diz,nomefile):
    with open(nomefile, "w") as f:
        for k, v in diz.iteritems():
            print >>f, k, v



def GeneraNuovoGrafo(tipo):
    if(tipo==0):
        graph= GeneraGrafoCaveman(2,3,True)
    else:
        graph= GeneraGrafoWaxman(12,0.47,0.47,True)

    PrintGrafoInJson(graph)
    nx.draw(graph, with_labels=True)
    plt.show()


def RunTest():
    graph= ReadGrafoDaJson('topology.json')
    
    BC_Cut = BrandesCutPoint(graph)

    PrintDizionarioToCsv(BC_Cut,"Cut_point.dat")

    os.system("sh C_scr.sh")
    os.system("gnuplot gnup_scr.sh")


'''
graph= ReadGrafoDaJson('topology.json')
nx.draw(graph, with_labels=True)
plt.show()
'''

#GeneraNuovoGrafo(1)
RunTest()
