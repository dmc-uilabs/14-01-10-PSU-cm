from pml import *
import logging
import networkx as nx
from idlelib import TreeWidget

#logging.basicConfig(level=logging.INFO)

# Initialize the system (ideally, this would already be in a database)
set_constant("Machinist :: Labor Rate", 59 * dollars / hour)
set_constant("Caster :: Labor Rate", 30 * dollars / hour)
set_constant("General Labor :: Labor Rate", 25 * dollars / hour)
set_constant("Welder :: Labor Rate", 40 * dollars / hour)
set_constant("X-Ray Machine :: Cost", 10 * dollars)
set_constant("Material :: Steel :: Cost", 0.5 * dollars / inch**3)
set_constant("Material :: Aluminum :: Cost", 0.8 * dollars / inch**3)
set_constant("Material :: Paint :: Cost", 0.2 * dollars / inch**2)

register_file("Make", "library/make.pml")
register_file("Make :: Purchase", "library/purchase.pml")
register_file("Make :: Fabricate", "library/fabricate.pml")
register_file("Make :: Fabricate :: Stock Machining", "library/machining.pml")
register_file("Make :: Fabricate :: Plate/Sheet", "library/plate.pml")
register_file("Make :: Fabricate :: Casting", "library/casting.pml")
register_file("Make :: Fabricate :: Paint", "library/painting.pml")
register_file("Assemble", "library/assembly.pml")
register_file("Assemble :: Welding", "library/welding.pml")
# register_file("Assemble :: Bolting", "library/bolting.pml")

# load structure from iFAB BOM
import os
import xml.etree.ElementTree as ET

path = r"examples/engine_assembly"
tree = ET.parse(os.path.join(path, "eBOM.xml"))
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
        if ad.find("mechanical") is not None:
            fastening_steps.append({ "method" : ad.find("mechanical/fasteningMethod").text,
                                     "quantity" : int(ad.find("mechanical/fasteningQuantity").text) })
        
    assemble_process = loaded_processes[subassembly.get("id")]
    assemble_process.set_predecessors(dependencies)
    setattr(assemble_process, "fasteningSteps", fastening_steps)
    
    print("Created assembly", loaded_processes[subassembly.get("id")].name, "with dependencies", dependencies)

deliver = Process(kind = "Deliver",
                  name = "Deliver",
                  level = "activity",
                  predecessor = [p for p in loaded_processes.values() if len(p.successors) == 0])

# Create and expand the process graph
processGraph = ProcessGraph(*loaded_processes.values(), deliver)
expand_graph(processGraph)

# # Save graph as image
as_png(processGraph, "graph.png")

# Validate the graph by ensuring routings exist
if validate_graph(processGraph):
    print("Graph is valid!")
      
    # Find the minimum cost
    print()
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(processGraph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
    (total_time, selected_processes) = find_min(processGraph, weight="time")
    print("    Quickest Configuration: %s" % as_time(total_time))
    (cp_time, selected_processes) = find_min(processGraph, weight="linearcomb")
    print("    Quickest Configuration: %s" % as_dollars(cp_time))
    # Save the minimum routings to a graph
    minimumGraph = create_subgraph(selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
      
else:
    print("Process graph is invalid - No routing exists")