import networkx as nx
from .units import *
import numpy
import re
from .analysis import *

levels = { "activity" : "red",
           "task" : "green",
           "operation" : "orange" }




def as_networkx(graph, weight="cost",simvar=1):
    processes = graph.processes
    graph = nx.DiGraph()
    
    if not hasattr(processes, "__iter__"):
        processes = [processes]
    
    # first create the nodes
    unprocessed = set()
    unprocessed.update(processes)
    processed = set()
    
    counter = 0
    id_map = {}
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        counter += 1
        
        #print("Adding node " + pick.name + " with id " + str(counter))
        id_map[pick] = str(counter)
        graph.add_node(pick)
        processed.add(pick)
        
        for successor in pick.successors:            
            if successor not in processed:
                unprocessed.add(successor)
                
    for node in processed:
        for successor in node.successors:
            if weight=="linearcomb":
                wv1=getattr(node,"cost") if hasattr(node,"cost") else 0; wv2=getattr(node,"time") if hasattr(node,"time") else 0
                weight_value=.5*(preprocv2(wv1,simvar,"cost"))+.5*(preprocv2(wv2,simvar,"time"))
            if weight=="cost":
                 tw = getattr(node, "cost") if hasattr(node, "cost") else 0
            #print("Adding edge between " + node.name + " and " + successor.name + " with weight " + str(weight_value))
                 weight_value=preprocv2(tw, simvar, weight)
            if weight=="time":
                 tw = getattr(node, "time") if hasattr(node, "time") else 0
            #print("Adding edge between " + node.name + " and " + successor.name + " with weight " + str(weight_value))
                 weight_value=preprocv2(tw, simvar, weight)     
            #print(weight_value)
            graph.add_edge(node, successor, **{weight : weight_value})
           
            
    return graph





def as_graph(processes):
    import pydotplus as pydot
    
    graph = pydot.Dot(graph_type="digraph")
    
    if not hasattr(processes, "__iter__"):
        processes = [processes]
    
    # first create the nodes
    unprocessed = set()
    unprocessed.update(processes)
    processed = set()
    
    counter = 0
    id_map = {}
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        counter += 1
        
        #print("Adding node " + pick.name + " with id " + str(counter))
        id_map[pick] = str(counter)
        node = pydot.Node(id_map[pick],
                          label=pick.name + (("[" + as_dollars(pick.cost) + "]") if hasattr(pick, "cost") else ""),
                          style="filled",
                          fillcolor=levels[pick.level] if hasattr(pick, "level") and pick.level in levels else "white")
        graph.add_node(node)
        processed.add(pick)
        
        for successor in pick.successors:            
            if successor not in processed:
                unprocessed.add(successor)
                
    for node in processed:
        for successor in node.successors:
            #print("Adding edge between " + node.name + " and " + successor.name)
            edge = pydot.Edge(id_map[node], id_map[successor])
            graph.add_edge(edge)
            
    return graph

def as_png(graph, file):
    graph = as_graph(graph.processes)
    graph.write_png(file)