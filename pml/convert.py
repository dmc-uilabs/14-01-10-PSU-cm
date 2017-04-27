import networkx as nx
from .units import as_dollars

levels = { "activity" : "red",
           "task" : "green",
           "operation" : "orange" }

def calc_weight(process, weight, default_weight = 0):
    if hasattr(weight, "__call__"):
        try:
            return weight(process)
        except:
            return default_weight
    elif hasattr(process, weight):
        return getattr(process, weight)
    else:
        return default_weight

def as_networkx(graph, weight="cost"):
    '''Converts a PML Graph to a NetworkX graph while assigning weights to the
       edges.'''
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
        
        id_map[pick] = str(counter)
        graph.add_node(pick)
        processed.add(pick)
        
        for successor in pick.successors:            
            if successor not in processed:
                unprocessed.add(successor)
                
    for node in processed:
        for successor in node.successors:
            weight_value = calc_weight(node, weight)
            graph.add_edge(node, successor, weight = weight_value)
            
    return graph

def as_graph(processes):
    '''Converts the given processes to a PyDot graph which can be displayed
       using GraphVis.'''
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
            edge = pydot.Edge(id_map[node], id_map[successor])
            graph.add_edge(edge)
            
    return graph

def as_png(graph, file):
    '''Saves the given PML Graph to a PNG image using GraphVis.'''
    graph = as_graph(graph.processes)
    graph.write_png(file)