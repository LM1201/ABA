import os;
import pygraphviz as pgv
os.environ["PATH"]= r'D:\Program Files\graphviz-2.38\release\bin;'+os.environ["PATH"];

def addNode(A,entity,nodes):
    nodeid= id(entity);
    name= str(entity);
    # print nodeid, name, type(entity)
    if nodeid not in nodes:
        A.add_node(name);
        nodes[nodeid]=entity;
    for child in entity.entities:
        addNode(A, child, nodes);
        A.add_edge(name, str(child));
    A.add_node(entity)

def buildGraph(tn,entityname):
    A=pgv.AGraph(directed=True,strict=True)
    entities=tn.Entities
    entity= entities[entityname]
    nodes={};
    addNode(A,entity,nodes);
    A.graph_attr['epsilon']='0.0001'
    print (A.string()) # print dot file to standard output
    A.write('foo.dot')
    A.layout('dot') # layout with dot
    A.draw('foo.png') # write to file


