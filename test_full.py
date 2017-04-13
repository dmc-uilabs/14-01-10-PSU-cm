from pml import *
import logging
import networkx as nx
import time

overall_start_time = time.time()

#logging.basicConfig(level=logging.INFO)

# Scan the library/ folder for __init__.pml files, which are
# executed to initialize the PML "database"
start_time = time.time()
auto_register("library")
print("Load PML Library Elapsed Time: %f s" % (time.time() - start_time))

# load structure from iFAB BOM
import os
import xml.etree.ElementTree as ET

path = r"examples/engine_assembly"
file = os.path.join(path, "eBOM.xml")
#file = r"examples/simpleExample.xml"

start_time = time.time()

tree = ET.parse(file)
root = tree.getroot()

# standard units used by iFAB converted into SymPy units
units = { "mm"  : mm,
          "mm2" : mm**2,
          "mm3" : mm**3,
          "kg"  : kg }

# load the individual parts
parts = root.find("parts")
loaded_parts = {}
loaded_processes = {}
instance_to_part = {}

for part in parts.findall("part"):
    for instance in part.findall("instances/instance"):
            instance_to_part[instance.get("instance_id")] = part.get("id")
    
    if part.find("manufacturingDetails/partClass") is not None:
        if part.find("manufacturingDetails/partClass").get("id") in ["Fabricated", "Rollup"]:
            continue
    
    loaded_part = Part(name = part.find("name").text,
                       id = part.get("id"),
                       length = float(part.find("length").text) * units[part.get("unit", "mm")],
                       width = float(part.find("width").text) * units[part.get("unit", "mm")],
                       height = float(part.find("height").text) * units[part.get("unit", "mm")],
                       surface_area = float(part.find("surface_area").text) * units[part.get("unit", "mm2")],
                       volume = float(part.find("volume").text) * units[part.get("unit", "mm3")],
                       weight = float(part.find("weight").text) * units[part.get("unit", "kg")])
    
    if part.find("manufacturingDetails/material") is not None:
        material = part.find("manufacturingDetails/material").text.lower()
        setattr(loaded_part, "material", "Steel" if "steel" in material else "Aluminum")
        
    if part.find("manufacturingDetails/price") is not None:
        setattr(loaded_part, "purchaseCost", float(part.find("manufacturingDetails/price").text) * dollars)
        
    if part.find("manufacturingDetails/leadTime") is not None:
        setattr(loaded_part, "leadTime", float(part.find("manufacturingDetails/leadTime").text) * days)
        
    for coating in part.findall("manufacturingDetails/coatings/coating"):
        setattr(loaded_part, "coating", coating.text)
        
    
    make_process = Process(kind = "Make",
                           name = "Make " + loaded_part.name,
                           level = "activity",
                           part = loaded_part)
    
    loaded_parts[loaded_part.id] = loaded_part
    loaded_processes[loaded_part.id] = make_process
    
    print("Loaded part " + loaded_part.name)

# load the subassemblies
assemblies = root.find("assemblies")
loaded_assemblies = {}

for subassembly in assemblies.findall("subassembly"):
    assemble_process = Process(kind = "Assemble",
                               name = subassembly.find("name").text,
                               id = subassembly.get("id"),
                               level = "activity")  
    
    loaded_processes[assemble_process.id] = assemble_process
     
for subassembly in assemblies.findall("subassembly"):
    dependencies = []
    fastening_steps = []
    
    for pr in subassembly.findall("contains/partRef"):
        id = pr.get("instance_id")
        
        if id not in loaded_processes:
            id = instance_to_part[id]

        dependencies.append(loaded_processes[id])
         
    for ad in subassembly.findall("assemblyDetails/assemblyDetail"):
        for elem in ad.findall("*"):
            if elem.tag == "mechanical":
                fastening_steps.append({ "method" : elem.find("fasteningMethod").text,
                                         "quantity" : int(elem.find("fasteningQuantity").text) })
            else:
                fastening_steps.append({ "method" : elem.tag })
        
    assemble_process = loaded_processes[subassembly.get("id")]
    assemble_process.set_predecessors(dependencies)
    setattr(assemble_process, "fasteningSteps", fastening_steps)
    
    print("Created assembly", loaded_processes[subassembly.get("id")].name, "with dependencies", dependencies)

deliver = Process(kind = "Deliver",
                  name = "Deliver",
                  level = "activity",
                  predecessor = [p for p in loaded_processes.values() if len(p.successors) == 0])

print("Load XML Elapsed Time: %f s" % (time.time() - start_time))

# Create and expand the process graph
processGraph = ProcessGraph(*loaded_processes.values(), deliver)

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