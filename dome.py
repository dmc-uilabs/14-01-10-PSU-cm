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
    processGraph = load_ebom(file)
    
    # Expand the process graph using the PML models
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