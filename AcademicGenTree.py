
# coding: utf-8

# In[1]:


import urllib.request
import re
import pydot
import networkx as nx
from lxml import etree
import html
import os


# In[2]:


class Matheux:

    def __init__(self, identifiant):
        
        
        self.identifiant = identifiant
        
        url = "https://www.genealogy.math.ndsu.nodak.edu/id.php?id="+str(identifiant)
        response = urllib.request.urlopen(url)
        htmlParser = etree.HTMLParser()
        tree = etree.parse(response, htmlParser)
        
        # Dirty scrapping
        self.nom = ['-'.join(s.split('-')[0:-1]).strip() for s in tree.xpath("//title/text()")][0]
        
        self.encadrants = [a.split('=')[1] for (a,b,c) in (zip(tree.xpath("//h2")[0]
                                                               .xpath("//p/a/@href"),
         tree.xpath("//h2")[0].xpath("//p/a/text()"),
         [e.xpath("../text()") for e in tree.xpath("//h2")[0].xpath("//p/a")]))
                           if 'Advisor' in ''.join(c)]
        
        self.doctorants = [s.split('=')[1] for s in tree.xpath('//div[@id="paddingWrapper"]')[0]
                           .xpath('//td/a/@href')]
        
        self.infos = [s.strip() for s in tree.xpath("//h2")[0]
                      .xpath("..//span/text()") if 'Dissertation:' not in s and s.strip() != '']
        
        self.label = ''.join(['<','<b>',self.nom,'</b>','<br/>']
                             +[html.escape(s)+'<br/>' for s in self.infos]
                             +['>'])
        
    def id(self):
        return int(self.identifiant)
    def __hash__(self):
        return self.id()
    def __eq__(self,other):
        return self.__hash__() == other.__hash__()


# In[3]:


racine = Matheux(201415) # 201415 est mon id sur www.genealogy.math.ndsu.nodak.edu
LIFOArray = [(None,racine)]

G = nx.DiGraph()

# On traite l'ascendance

while (len(LIFOArray) > 0):
    m = LIFOArray.pop(0)
    doctorant = m[0]
    noeudCourant = m[1]

    flag_traite = False
    if (noeudCourant not in G):
        G.add_node(noeudCourant, label=noeudCourant.label)
    else:
        flag_traite = True
    
    # On relie le doctorant à l'encadrant
    if doctorant is not None:
        G.add_edge(noeudCourant, doctorant)
    
    # On enfile les encadrants pour traitement en mémorisant le doctorants
    # qu'ils ont encadré
    if not flag_traite:
        for e in noeudCourant.encadrants:
            LIFOArray.append((noeudCourant,Matheux(e)))

# On traite la descendance
            
LIFOArray = [(Matheux(r),racine) for r in racine.doctorants]
while (len(LIFOArray) > 0):
    m = LIFOArray.pop(0)
    encadrant = m[1]
    noeudCourant = m[0]
    
    G.add_node(noeudCourant, label=noeudCourant.label)
    G.add_edge(encadrant, noeudCourant)
    
    for e in noeudCourant.doctorants:
        LIFOArray.append((Matheux(e),noeudCourant))


# In[4]:


nx.nx_pydot.write_dot(G,'pierre.dot')
get_ipython().system('dot -Tpdf pierre.dot > pierre.pdf')

