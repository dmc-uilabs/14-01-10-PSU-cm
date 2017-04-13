from pml import *
import logging
import networkx as nx
import time

overall_start_time = time.time()

#logging.basicConfig(level=logging.INFO)

# Scan the library/ folder and its subfolders for __init__.pml files, which are
# executed to initialize the PML "database"
start_time = time.time()
auto_register("library")
print("Load PML Library Elapsed Time: %f s" % (time.time() - start_time))

# Load the eBOM.xml file
path = r"examples/engine_assembly"
file = os.path.join(path, "eBOM.xml")
#file = r"examples/simpleExample.xml"

start_time = time.time()
processGraph = load_ebom(file)
print("Load XML Elapsed Time: %f s" % (time.time() - start_time))

# Expand the process graph using the PML models
start_time = time.time()
expand_graph(processGraph)
print("Expand Graph Elapsed Time: %f s" % (time.time() - start_time))

# # Save graph as image
start_time = time.time()
as_png(processGraph, "graph.png")
print("Save PNG Elapsed Time: %f s" % (time.time() - start_time))

# Validate the graph by ensuring routings exist
if validate_graph(processGraph):
    print()
    print("Graph is valid!")
      
    # Find the minimum cost
    start_time = time.time()
    print()
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(processGraph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
    print("    Elapsed Time: %f s" % (time.time() - start_time))
    
    start_time = time.time()
    print()
    print("-- Find quickest configuration --")
    (total_time, selected_processes) = find_min(processGraph, weight="time")
    print("    Quickest Configuration: %s" % as_time(total_time))
    print("    Elapsed Time: %f s" % (time.time() - start_time))
    
    start_time = time.time()
    print()
    print("-- Find best 50/50 configuration --")
    (cp_time, selected_processes) = find_min(processGraph, weight="linearcomb")
    print("    Best Configuration: %s" % str(cp_time))
    print("    Elapsed Time: %f s" % (time.time() - start_time))
    
    # Save the minimum routings to a graph
    minimumGraph = create_subgraph(selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
    
    # Save the minimum routings to a graph
    start_time = time.time()
    print()
    print("-- Saving cheapest configuration to PNG --")
    minimumGraph = create_subgraph(selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
    print("    Elapsed Time: %f s" % (time.time() - start_time))
    
    # Determine the resources required
    print()
    print("-- Resources required by configuration --")
    print("   ", create_resources(selected_processes))
      
else:
    print()
    print("Process graph is invalid - No routing exists")
    
print()
print("Overall Elapsed Time: %f s" % (time.time() - overall_start_time))