import os
import shutil
import wget
import json
import logging
import tempfile
import traceback
import xml.etree.ElementTree as ET
import networkx as nx
from pml import *

#logging.basicConfig(level=logging.INFO)

def get_file(file, delete_on_exit = []):    
    # due to current limitations of DMC, allow shortened URLs
    if "://" not in file:
        file = "http://" + file
        
    if file.startswith("file://"):
        return file[7:]
    else:
        # create temp file to store the file contents
        fd, tmpfile = tempfile.mkstemp()
        os.close(fd)
        os.unlink(tmpfile)
        
        # download the file contents
        wget.download(file.replace("?dl=0", "?dl=1"), tmpfile)
        delete_on_exit.append(tmpfile)
        return tmpfile

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
            if len(line.strip()) > 0:
                tokens = line.split("=")
                inputs[tokens[0].strip()] = tokens[1].strip()
                
    return inputs
            
def validate_inputs(inputs, fields):
    for name, (required, type) in fields.items():
        if required and name not in inputs:
            fail("missing required input " + str(name))
            
        if name in inputs:
            inputs[name] = type(inputs[name])
            
    return inputs

def process(input_file, user_constants=None, weight="cost"):    
    # Initialize the system
    auto_register("library")
    
    # Update system with user-defined constants
    if user_constants is not None:
        load_constants(user_constants)
    
    # Load structure from iFAB BOM    
    processGraph = load_ebom(input_file)
    
    # Expand the process graph using the PML models
    expand_graph(processGraph)
    
    # Save graph as image
    as_png(processGraph, "graph.png")
    
    # Validate the graph by ensuring routings exist
    if validate_graph(processGraph):
        # Find the routing that optimizes the user-defined weight (e.g., cost or time)
        (_, selected_processes) = find_min(processGraph, weight=weight)
        minimumGraph = create_subgraph(processGraph, selected_processes)
        
        # Save the minimum routings to a graph
        as_png(minimumGraph, "minimumGraph.png")
        
        # Compute the cost and time
        total_cost = sum_weight(minimumGraph, weight="cost")
        total_time = sum_weight(minimumGraph, weight="time")
        
        # Output the results
        write_outputs("output.txt", { "message" : "Design is manufacturable",
                                      "cost" : float(total_cost / dollars),
                                      "time" : float(total_time / days) })       
    else:
        fail("Unable to manufacture design, no routings exist")
  
if __name__ == "__main__":
    try:
        INPUT_DEFN = { "inputFile" : (True, str), "userConstants" : (False, str), "optimizeWeight" : (False, str)}
        
        # read and validate the inputs from DOME
        inputs = read_inputs("input.txt")
        inputs = validate_inputs(inputs, INPUT_DEFN)
    
        # convert inputs to kwargs, track any temporary files
        kwargs = {}
        delete_on_exit = []
        
        kwargs["input_file"] = get_file(inputs["inputFile"], delete_on_exit)
        
        if "userConstants" in inputs:
            kwargs["user_constants"] = get_file(inputs["userConstants"], delete_on_exit)
            
        if "optimizeWeight" in inputs:
            kwargs["weight"] = inputs["optimizeWeight"]
            
        # process the submission
        process(**kwargs)
        
        # delete the temporary files
        for file in delete_on_exit:
            os.unlink(file)
    except Exception as e:
        traceback.print_exc()
        fail("An error occurred: " + str(e))  