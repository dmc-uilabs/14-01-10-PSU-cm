from pml import *
import logging
import networkx as nx

#logging.basicConfig(level=logging.INFO)

# Initialize the system
auto_register("library")

# Create an example two part assembly
partA = Part(name = "Part A",
             length = 5 * inches,
             width = 2 * inches,
             height = 7 * inches,
             purchaseCost = 5 * dollars,
             volume = 38 * inches**3,
             surface_area = 28 * inches**2,
             material = "Steel")

partB = Part(name = "Part B",
             length = 5 * inches,
             width = 10 * inches,
             height = 0.5 * inches,
             volume = 20 * inches**3,
             surface_area = 100 * inches**2,
             material = "Steel")

makeA = Process(kind = "Make",
                name = "Make A",
                level = "activity",
                part = partA)

makeB = Process(kind = "Make",
                name = "Make B",
                level = "activity",
                part = partB)

assemble = Process(kind = "Assemble",
                   name = "Assemble A to B",
                   level = "activity",
                   predecessor = [makeA, makeA, makeB],
                   fasteningSteps = [{ "method" : "weld",
                                       "weldLength" : 5 * inches },
                                     { "method" : "paint" }])

deliver = Process(kind = "Deliver",
                  name = "Deliver",
                  level = "activity",
                  predecessor = assemble)

# Create and expand the process graph
processGraph = ProcessGraph(makeA, makeB, assemble, deliver)
expand_graph(processGraph)

# Save graph as image
as_png(processGraph, "graph.png")

# Validate the graph by ensuring routings exist
if validate_graph(processGraph):
    print("Graph is valid!")
    
    # Find the minimum cost
    print()
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(processGraph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
    
    # Save the minimum routings to a graph
    minimumGraph = create_subgraph(selected_processes)
    as_png(minimumGraph, "minimumGraph.png")

    # Convert to networkx graph (with cost weights on edges)
    network = as_networkx(processGraph, weight="cost")
    
    # Find cheapest cost routings
    print()
    print("-- Find cheapest routings demo --")
    for source in processGraph.get_sources():
        path = nx.shortest_path(network, source, assemble, weight="cost")
        
        print("    Cheapest route for %s:" % source.name)
        print("        Routing: %s" % path)
        print("        Cost: %s" % as_dollars(sum([p.cost if hasattr(p, "cost") else 0 for p in path])))
        print("        Time: %s" % as_time(sum([p.time if hasattr(p, "time") else 0 for p in path])))
        
    # Find all routings for making Part A
    print()
    print("-- Find all possible routings demo -- ")
    paths = nx.all_simple_paths(network, makeA, assemble)
    
    for path in paths:
        print("    Possible path for %s:" % makeA.name)
        print("        Routing: %s" % path)
        print("        Cost: %s" % as_dollars(sum([p.cost if hasattr(p, "cost") else 0 for p in path])))
        print("        Time: %s" % as_time(sum([p.time if hasattr(p, "time") else 0 for p in path])))
    
else:
    print("Process graph is invalid - No routing exists")