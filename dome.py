import os
import shutil
import wget
import json
import logging
import traceback
import xml.etree.ElementTree as ET
import networkx as nx
from pml import *

#logging.basicConfig(level=logging.INFO)

def write_outputs(file, fields):
    with open(file, "w") as f:
        for name, value in fields.items():
            f.write(str(name) + " = " + str(value))
            f.write("\n")

def fail(message):
    write_outputs("output.txt", { "message" : message})
    exit(-1)

def read_inputs(file):
    inputs = {}

    with open(file, "r") as f:
        for line in f:
            tokens = line.split("=")
            inputs[tokens[0].strip()] = tokens[1].strip()
            
def validate_inputs(inputs, fields):
    for name, (required, type) in fields.items():
        if required and name not in inputs:
            fail("missing required input " + str(name))
            
        if name in inputs:
            inputs[name] = type(inputs[name])
            
    return inputs

def process(file):    
    # Initialize the system
    auto_register("library")
    
    # Load structure from iFAB BOM    
    tree = ET.parse(file)
    root = tree.getroot()
    
    # Standard units used by iFAB converted into SymPy units
    units = { "mm"  : mm,
              "mm2" : mm**2,
              "mm3" : mm**3,
              "kg"  : kg }
    
    # Load the individual parts
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
    
    # Load the subassemblies
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
    
    # Create the sink node
    deliver = Process(kind = "Deliver",
                      name = "Deliver",
                      level = "activity",
                      predecessor = [p for p in loaded_processes.values() if len(p.successors) == 0])
    
    # Create and expand the process graph
    processGraph = ProcessGraph(*loaded_processes.values(), deliver)
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
        
        write_outputs("output.txt", { "message" : "Design is manufacturable", "cost" : float(total_cost / dollars) })       
    else:
        fail("Unable to manufacturing design, no routings exist")
  
if __name__ == "__main__":
    try:
        INPUT_DEFN = { "inputFile" : (True, str)}
        
        inputs = read_inputs("input.txt")
        inputs = validate_inputs(inputs, INPUT_DEFN)
    
        # due to input length limit, might need to add prefix
        if "://" not in inputs["inputFile"]:
            inputs["inputFile"] = "http://" + inputs["inputFile"]
    
        # download the file
        wget.download(inputs["inputFile"].replace("?dl=0", "?dl=1"), "eBOM.xml")
    
        # process the design to find the cheapest routing
        process("eBOM.xml")
    except Exception as e:
        traceback.print_exc()
        fail("An error occurred: " + str(e))  