import copy
import logging
import networkx as nx
from .library import *
from .units import *
from .exceptions import *
from .convert import *
from .analysis import *

LOGGER = logging.getLogger("PML")

# WARNING: replace must follow a breadth-first pattern to ensure successor links update correctly before
# dependent nodes potentially change
def replace(parent, sources, sinks = None):
    if not hasattr(sources, "__iter__"):
        sources = [sources]
    
    if sinks is None:
        sinks = set()
        
        unprocessed = list()
        unprocessed.extend(sources)
        processed = set()
        
        while len(unprocessed) > 0:
            pick = unprocessed.pop(0)
            processed.add(pick)
            
            possible_successors = [s for s in pick.successors if s not in processed]
            
            if len(possible_successors) > 0:
                for successor in pick.successors:
                    unprocessed.append(successor)
            else:
                sinks.add(pick)
                
    for sink in sinks:
        #print("Updating sink", sink, "with", parent.successors)
        old_successors = sink.successors.copy()
        sink.set_successors(parent.successors)
        
        for successor in old_successors:
            sink.add_successor(successor)
        
    parent.set_successors(sources) 
    
    
def prune_leaves(process):
    unprocessed = set()
    unprocessed.add(process)
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        
        if len(pick.successors) == 0:
            for p in pick.predecessors.copy():
                unprocessed.add(p)
                pick.remove_predecessor(p)

def expand(process):
    if process.expanded:
        return
    
    LOGGER.info("Expanding node, kind=%s, name=%s", process.kind, process.name)
    
    try:
        matches = lookup(process.kind)
        
        env = { "parent" : process }
        
        if matches is None:
            LOGGER.info("No process models found, no further expansion possible")
        else:
            LOGGER.info("Found %d process models", len(matches))
            for match in matches:
                try:
                    LOGGER.info("Applying process model, %s", match)
                    eval(match, env, globals())
                except FailedRouting as e:
                    LOGGER.warning("Routing failed, kind=%s, name=%s, message=%s", process.kind, process.name, e.args[0])
                    process.set_successors([])
                    prune_leaves(process)
    except KeyError:
        pass
    
    process.expanded = True
            
def expand_all(process):
    unprocessed = set()
    unprocessed.add(process)
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        expand(pick)
        unprocessed.update(enumerate_successors(pick))
        
def expand_graph(graph, create_copy = False):
    modified_graph = copy.deepcopy(graph) if create_copy else graph
    
    for process in modified_graph.processes:
        expand_all(process)
        
    return modified_graph

def validate_graph(graph, networkx = None):
    if networkx is None:
        networkx = as_networkx(graph)
        
    LOGGER.info("Validating graph")
    
    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in original_process.successors:
            new_successor = graph.original_processes[original_successor]
            LOGGER.info("Checking for path between %s and %s", new_process.name, new_successor.name)
            
            if not nx.has_path(networkx, new_process, new_successor):
                LOGGER.info("No path found")
                LOGGER.warn("No path found between %s and %s", new_process.name, new_successor.name)
                return False
            else:
                LOGGER.info("Path found")
                
    return True

def find_min(graph, weight = None, networkx = None, simvar=None):
    total = 0
    selected_processes = set()
    
    if weight is None:
        weight = "cost"
    
    if networkx is None:
        networkx = as_networkx(graph, weight = weight, simvar=simvar)
    
    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in original_process.successors:
            new_successor = graph.original_processes[original_successor]
            path = nx.shortest_path(networkx, new_process, new_successor, weight = weight)
            
            selected_processes.update(path)
            total += sum([getattr(p, weight) if hasattr(p, weight) else 0 for p in path])
                
    return (total, selected_processes)





    
def enumerate_successors(process, processed = set()):
    result = set()
    
    for successor in process.successors:
        if successor not in processed:
            result.add(successor)
            processed.add(successor)
            
            result.update(enumerate_successors(successor, processed))
        
    return result

def create_subgraph(processes):
    processes = set(copy.deepcopy(processes))
    
    for process in processes:
        for successor in list(process.successors):
            if successor not in processes:
                process.remove_successor(successor)
        for predecessor in list(process.predecessors):
            if predecessor not in processes:
                process.remove_predecessor(predecessor)
                
    return ProcessGraph(*processes)

class Part(object):
    
    def __init__(self, name, **kwargs):
        self.name = name
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
class ProcessGraph(object):
    
    def __init__(self, *processes):
        self.processes = processes
        
        # the original_processes attribute stores the unexpanded processes; each successor edge
        # between original_processes must have a corresponding path through the expanded processes
        # in order to be valid
        self.original_processes = {}
        
        memo = {}
        for process in processes:
            self.original_processes[copy.deepcopy(process, memo)] = process
        
    def get_sources(self):
        return [p for p in self.processes if len(p.predecessors) == 0]
    
    def get_sinks(self):
        return [p for p in self.processes if len(p.successors) == 0]

class Process(object):
    
    def __init__(self, kind, predecessor=None, successor=None, **kwargs):
        super(Process, self).__init__()
        self.kind = kind
        self.predecessors = list()
        self.successors = list()
        self.expanded = False
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        if predecessor is not None:
            if hasattr(predecessor, "__iter__"):
                for p in predecessor:
                    self.add_predecessor(p)
            else:
                self.add_predecessor(predecessor)
        
        if successor is not None:  
            if hasattr(successor, "__iter__"):
                for s in successor:
                    self.add_successor(s)
            else:
                self.add_successor(successor)

    def add_successor(self, successor):
        self.successors.append(successor)
        successor.predecessors.append(self)
            
    def add_predecessor(self, predecessor):
        self.predecessors.append(predecessor)
        predecessor.successors.append(self)
            
    def remove_successor(self, successor):
        self.successors.remove(successor)
        successor.predecessors.remove(self)
            
    def remove_predecessor(self, predecessor):
        self.predecessors.remove(predecessor)
        predecessor.successors.remove(self)
            
    def set_successor(self, successor):
        self.set_successors([successor])
        
    def set_predecessor(self, predecessor):
        self.set_predecessors([predecessor])
            
    def set_successors(self, successors):
        for successor in list(self.successors):
            self.remove_successor(successor)
        
        for successor in successors:
            self.add_successor(successor)
            
    def set_predecessors(self, predecessors):
        for predecessor in list(self.predecessors):
            self.remove_predecessor(predecessor)
            
        for predecessor in predecessors:
            self.add_predecessor(predecessor)
            
    def __repr__(self):
        return "Process[" + self.kind + "]"
            
class Resource(object):
    
    def __init__(self, name, quantity, requires = []):
        self.name = name
        self.quantity = quantity
        self.requires = requires