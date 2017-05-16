#!/usr/bin/python3

from pml import *
import logging
import networkx as nx
from pylab import figure, axes, pie, title, show
import matplotlib
from matplotlib import pyplot as plt




def gen_tradespace(process_graph):

    for x in range (0, 10):
        for y in range (0, 10):
            var_x = (x/10)
            var_y = (y/10)
            print ("x=" + str(var_x) + ", y=" + str(var_y))
            #(cp_time, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
            (cp_time, selected_processes) = find_min(process_graph, weight=lambda n : var_x*n.cost/dollars + var_y*n.time/days)
            X[x] = 


    X = [590,540,740,130,810,300,320,230,470,620,770,250]
    Y = [32,36,39,52,61,72,77,75,68,57,48,48]

    plt.scatter(X,Y)

    plt.savefig('tradespace.png')


# Scan the library/ folder and its subfolders for __init__.pml files, which are
# executed to initialize the PML "database"
auto_register("library")

# Load the eBOM.xml file
path = r"examples/engine_assembly"
file = os.path.join(path, "eBOM.xml")
file = r"examples/simpleExample.xml"

process_graph = load_ebom(file, build_quantity=50)

# Expand the process graph using the PML models
expand_graph(process_graph)

# # Save graph as image
as_png(process_graph, "graph.png")

# Validate the graph by ensuring routings exist
if validate_graph(process_graph):
    print()
      
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(process_graph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
     
    print()
    print("-- Find quickest configuration --")
    (total_time, selected_processes) = find_min(process_graph, weight="time")
    print("    Quickest Configuration: %s" % as_time(total_time))
     
    print()
    print("-- Find best 50/50 configuration --")
    (cp_time, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
    print("    Best Configuration: %s" % str(cp_time))
    
    print()
    print("-- Saving configuration to PNG --")
    minimumGraph = create_subgraph(process_graph, selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
    
    print()
    print("-- Resources required by configuration --")
    print("   ", create_resources(selected_processes))

    gen_tradespace(process_graph)
      
else:
    print()
    print("Process graph is invalid - No routing exists")
    
