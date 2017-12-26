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


# Genera un grafo networkx leggendo da un file in formato NetJSON
#@url il percorso del file da leggere
def ReadGrafoDaJson(url):
    netJSON = NetJsonParser(file=url)
    grafo = netJSON.graph
    return grafo


# Print su file (topology.json) in formato NetJSON del grafo passato come argomento
#@G un grafo networkx
#@njproto il protocollo da inserire nell'intestazione del file NetJSON
#@njversion la versione da inserire nell'intestazione del file NetJSON
#@njrevision id revisione da inserire nell'intestazione del file NetJSON
#@njmetric la metrica da inserire nell'intestazione del file NetJSON
def PrintGrafoInJson(G, njproto='OLSR', njversion='0.1', njrevision='a09z',
                     njmetric='ETX'):
    js = to_netjson(njproto,
                    njversion,
                    njrevision,
                    njmetric,
                    G.nodes(data=True),
                    G.edges(data=True), dict=True)
    f1 = open('./topology.json', 'w+')
    f1.write(json.dumps(js, indent=4))
    f1.close()


# Genera un grafo di tipo Caveman connesso e con archi pesati.
#@num numero di gruppi
#@size dimensione dei gruppi
#@randWeight se True i pesi degli archi hanno valori nell'intervallo [1.0 , 1.1)
#@return un grafo di tipo Caveman
def GeneraGrafoCaveman(num, size, randWeight=False):
    G = nx.connected_caveman_graph(num, size)
    for u, v, d in G.edges(data=True):
        if(randWeight == False):
            d['weight'] = 1
        else:
            d['weight'] = np.random.uniform(1.0, 1.1)
    return G


# Genera un grafo di tipo Waxman con archi pesati.
# Each pair of nodes at distance d is joined by an edge with probability
#   p=b*exp(-d/aL)
#@num numero di nodi
#@a= alpha parametro nella formula della probabilita
#@b= beta parametro nella formula della probabilita
#@randWeight se True i pesi degli archi hanno valori nell'intervallo [1.0 , 1.1)
#@return un grafo di tipo Waxman
def GeneraGrafoWaxman(num, b=0.4, a=0.1, randWeight=False):
    G = nx.waxman_graph(num, beta=b, alpha=a)
    for u, v, d in G.edges(data=True):
        if(randWeight == False):
            d['weight'] = 1
        else:
            d['weight'] = np.random.uniform(1.0, 1.1)
    return G


# Funzione per il calcolo della betweenness centrality di un grafo.
# la BC per i cut-point e' ottenuta dalla somma delle BC calcolata su ogni componente biconnessa a
# cui appartiene, per tutti gli altri nodi e' calcolata normalmente con l'algoritmo standard
#@G grafo su cui calcolare la BC
#@return dictionary (nodo,BC)
def BrandesCutPoint(g):
    # per compatibilita' con libreria C, rimuvo eventali nodi sconnessi
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
            h = nx.Graph(g)
            for altrebcs in bconns:
                if(altrebcs != bcs):
                    rimuovi = altrebcs.nodes()
                    rimuovi.remove(p)
                    h.remove_nodes_from(rimuovi)
            b = nx.betweenness_centrality(h, weight='weight', endpoints=False,
                                          normalized=False)[p]
            bc[p] += b
        bc[p] += (n_nodes - 1)
    for n, b in nx.betweenness_centrality(g, weight='weight', endpoints=True,
                                          normalized=False).iteritems():
        if n not in ap:
            bc[n] = b
    return bc


# Scrive su file specificato un dizionario, nel formato:" chiave valore "
#@diz il dizionario che si desidera esportare su file
#@nomefile il nome da dare al file contenete il dizionario
def PrintDizionarioToCsv(diz, nomefile):
    with open(nomefile, "w") as f:
        for k, v in diz.iteritems():
            print >>f, k, v


# Funzione ausiliaria per il test
def GeneraNuovoGrafo(tipo):
    if(tipo == 0):
        graph = GeneraGrafoCaveman(2, 3, True)
    else:
        graph = GeneraGrafoWaxman(12, 0.47, 0.47, True)

    PrintGrafoInJson(graph)
    nx.draw(graph, with_labels=True)
    plt.show()


# Funzione ausiliaria per il test
def RunTest():
    graph = ReadGrafoDaJson('topology.json')

    BC_Cut = BrandesCutPoint(graph)

    PrintDizionarioToCsv(BC_Cut, "Cut_point.dat")

    os.system("sh C_scr.sh")
    os.system("gnuplot gnup_scr.sh")


'''
graph= ReadGrafoDaJson('topology.json')
nx.draw(graph, with_labels=True)
plt.show()
'''

# GeneraNuovoGrafo(1)
RunTest()
