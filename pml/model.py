import copy
import logging
import itertools
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

def find_min(graph, weight = None, networkx = None):
    total = 0
    selected_processes = set()
    
    if weight is None:
        weight = "cost"
    
    if networkx is None:
        networkx = as_networkx(graph, weight = weight)
    
    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in original_process.successors:
            new_successor = graph.original_processes[original_successor]
            path = nx.shortest_path(networkx, new_process, new_successor, weight = "weight")
            
            selected_processes.update(path)
            
            for p in path:
                total += calc_weight(p, weight)
                
    return (total, selected_processes)

def generate_alternatives(graph, weights = None, networkx = None):
    if weights is None:
        weights = ["cost", "time"]
        
    if not isinstance(weights, (list, tuple)):
        weights = [weights]
    
    if networkx is None:
        networkx = as_networkx(graph)
        
    all_paths = []
    
    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in set(original_process.successors):
            new_successor = graph.original_processes[original_successor]
            all_paths.append(nx.all_simple_paths(networkx, new_process, new_successor))
              
    for product in itertools.product(*all_paths):
        selected_processes = set()
        
        for p in product:
            selected_processes.update(p)
            
        minimumGraph = create_subgraph(graph, selected_processes)
        
        yield [sum_weight(minimumGraph, weight=w) for w in weights]
        
def dominance_check(a, b):
    if len(a) != len(b):
        raise ValueError("lengths not the same")
    
    dominate1 = False
    dominate2 = False
    equal = True
        
    for i in range(len(a)):
        if a[i] < b[i]:
            dominate1 = True
            equal = False
        elif a[i] > b[i]:
            dominate2 = True
            equal = False

    if equal:
        return -1

    if dominate1 == dominate2:
        return 0
    elif dominate1:
        return -1
    else:
        return 1
        
def pareto(entries):
    result = []
    
    for e in list(entries):
        flags = [dominance_check(e, s) for s in result]
        dominates = [x > 0 for x in flags]
        nondominated = [x == 0 for x in flags]
        
        if any(dominates):
            continue
        else:
            result = list(itertools.compress(result, nondominated)) + [e]

    return result
        

def sum_weight(graph, weight = None, networkx = None):
    total = 0
    
    if weight is None:
        weight = "cost"
        
    if networkx is None:
        networkx = as_networkx(graph, weight = weight)

    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in original_process.successors:
            new_successor = graph.original_processes[original_successor]
            paths = nx.all_simple_paths(networkx, new_process, new_successor)
            
            # only select paths that do not include any intermediate original_processes
            valid_paths = []
            
            for path in paths:
                if not any([p in graph.original_processes.values() for p in path[1:-1]]):
                    valid_paths.append(path)

            # throw an error if there is anything but a single unique path
            if len(valid_paths) == 0:
                raise NoPathException("no path exists between nodes")
            elif len(valid_paths) > 1:
                raise MultiplePathException("multiple paths exist between nodes, reduce graph first")
            
            # sum up the weights
            for p in valid_paths[0]:
                total += calc_weight(p, weight)
                
    return total
    
def enumerate_successors(process, processed = set()):
    result = set()
    
    for successor in process.successors:
        if successor not in processed:
            result.add(successor)
            processed.add(successor)
            
            result.update(enumerate_successors(successor, processed))
        
    return result

def create_subgraph(graph, processes):
    # we want the original_processes of the subgraph to match those of the original graph; we use the Python
    # deepcopy memo to map from the original process to the copied process.
    memo = {}
    processes = set(copy.deepcopy(processes, memo))
    
    for process in processes:
        for successor in list(process.successors):
            if successor not in processes:
                process.remove_successor(successor)
        for predecessor in list(process.predecessors):
            if predecessor not in processes:
                process.remove_predecessor(predecessor)
                
    subgraph = ProcessGraph(*processes)
    subgraph.original_processes = {p : memo[id(graph.original_processes[p])] for p in graph.original_processes.keys()}
    return subgraph

def create_resources(processes, attr="resource"):
    '''Scans all of the processes for the given attribute, which can either be a
    value, a list of values, or a dictionary mapping values to their quantity.  If
    a value or a list of values is given, we assume the quantity is 1 (we don't
    currently check if the value appears multiple times in a list).'''
    resource_map = {}
    
    for process in processes:
        if hasattr(process, attr):
            resources = getattr(process, attr)
            
            if isinstance(resources, (list, tuple)):
                for resource in resources:
                    resource_map[resource] = max(1, resource_map.get(resource, 1))
            elif isinstance(resources, dict):
                for k, v in resources.items():
                    resource_map[k] = max(resource_map.get(k, 0), v)
            else:
                resource_map[resources] = max(1, resource_map.get(resources, 1))
                
    return resource_map

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
