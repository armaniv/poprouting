import networkx as nx
from netdiff import NetJsonParser
from netdiff.utils import _netjson_networkgraph as to_netjson
import json
import matplotlib.pyplot as plt
import numpy as np
import os


#Genera un grafo networkx leggendo da un file in formato NetJSON
#@url il percorso del file da leggere
def ReadGrafoDaJson(url):
    netJSON = NetJsonParser(file=url)
    grafo = netJSON.graph
    return grafo



#Print su file (topology.json) in formato NetJSON del grafo passato come argomento
#@G un grafo networkx
#@njproto il protocollo da inserire nell'intestazione del file NetJSON
#@njversion la versione da inserire nell'intestazione del file NetJSON
#@njrevision id revisione da inserire nell'intestazione del file NetJSON
#@njmetric la metrica da inserire nell'intestazione del file NetJSON
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



#Genera un grafo di tipo Caveman connesso e con archi pesati.
#@num numero di gruppi
#@size dimensione dei gruppi
#@randWeight se impostato a True i pesi degli archi hanno valori nell'intervallo [1.0 , 1.1)
#@return un grafo di tipo Caveman
def GeneraGrafoCaveman(num,size,randWeight=False):
    G = nx.connected_caveman_graph(num, size)
    for u,v,d in G.edges(data=True):
        if(randWeight==False):
            d['weight']=1
        else:
            d['weight']=np.random.uniform(1.0,1.1)
    return G



#Genera un grafo di tipo Waxman con archi pesati.
#https://networkx.github.io/documentation/stable/reference/generated/networkx.generators.geometric.waxman_graph.html#networkx.generators.geometric.waxman_graph
#Each pair of nodes at distance d is joined by an edge with probability
#   p=b*exp(-d/aL)
#@num numero di nodi
#@a= alpha parametro nella formula della probabilita
#@b= beta parametro nella formula della probabilita
#@randWeight se impostato a True i pesi degli archi hanno valori nell'intervallo [1.0 , 1.1)
#@return un grafo di tipo Waxman
def GeneraGrafoWaxman(num,b=0.4,a=0.1,randWeight=False):
    G = nx.waxman_graph(num,beta=b,alpha=a)
    for u,v,d in G.edges(data=True):
        if(randWeight==False):
            d['weight']=1
        else:
            d['weight']=np.random.uniform(1.0,1.1)
    return G



#Funzione per il calcolo della betweenness centrality di un grafo
#la BC per i cut-point e' ottenuta dalla somma delle BC calcolata su ogni componente biconnessa a
#cui appartiene, per tutti gli altri nodi e' calcolata normalmente con l'algoritmo standard
#@G grafo su cui calcolare la BC
#@return dictionary (nodo,BC)
def  BrandesCutPoint(G):
    keydoppie = list(nx.articulation_points(G))
    key= list(set(keydoppie))                                       #lista contentei i cut-point

    print key
    val_cutpoint= dict([(i, 0.0) for i in key])                     #creo un diz che contiene solo i cutpoint

    n=len(G)
    if(n>2):
        fattnormal= 2.0/((n-1)*(n-2))                               #calcolo fattore normalizzazione
    else:
        fattnormal= 1.0

    bicomp = list(nx.biconnected_component_subgraphs(G))

    for cc in bicomp:                                               #scandisco comp biconn e calcolo BC
        subBC = nx.betweenness_centrality(cc,endpoints=True,weight='weight',normalized=False)
        for i in key:                                               #scandisco cut-point
            if (i in subBC):                                        #se un cutpoin e' presente
                val_cutpoint[i]+=(subBC[i]*fattnormal)

    BC = nx.betweenness_centrality(G,endpoints=True,weight='weight')

    for i in key:
        BC[i]=val_cutpoint[i]

    return BC



#Scrive su file specificato un dizionario, nel formato:" chiave valore "
#@diz il dizionario che si desidera esportare su file
#@nomefile il nome da dare al file contenete il dizionario
def PrintDizionarioToCsv(diz,nomefile):
    with open(nomefile, "w") as f:
        for k, v in diz.iteritems():
            print >>f, k, v



#Funzione ausiliaria per il test
def GeneraNuovoGrafo(tipo):
    if(tipo==0):
        graph= GeneraGrafoCaveman(3,4,True)
    else:
        graph= GeneraGrafoWaxman(10,0.60,0.60,True)

    PrintGrafoInJson(graph)
    nx.draw(graph, with_labels=True)
    plt.show()

#Funzione ausiliaria per il test
def RunTest():
    graph= ReadGrafoDaJson('topology.json')

    BC_Cut = BrandesCutPoint(graph)

    PrintDizionarioToCsv(BC_Cut,"Cut_point.dat")

    os.system("sh C_scr.sh")
    os.system("gnuplot gnup_scr.sh")



#GeneraNuovoGrafo(0)
RunTest()
