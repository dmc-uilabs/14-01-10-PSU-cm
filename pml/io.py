import os
import logging
import xml.etree.ElementTree as ET
from .units import *
from .model import *

LOGGER = logging.getLogger("PML")

def load_ebom(file, build_quantity = 1):
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
                           weight = float(part.find("weight").text) * units[part.get("unit", "kg")],
                           quantity = build_quantity*sum([1 for _ in part.findall("instances/instance")]))
        
        if part.find("manufacturingDetails/material") is not None:
            material = part.find("manufacturingDetails/material").text.lower()
            setattr(loaded_part, "material", "Steel" if "steel" in material else "Aluminum")
            
        # old format for passing purchasing information
        if part.find("manufacturingDetails/price") is not None:
            setattr(loaded_part, "purchaseCost", float(part.find("manufacturingDetails/price").text) * dollars)
            
        if part.find("manufacturingDetails/leadTime") is not None:
            setattr(loaded_part, "leadTime", float(part.find("manufacturingDetails/leadTime").text) * days)
            
        # new format, which allows multiple supplier options with bulk quantities
        suppliers = []
        
        for supplier in part.findall("manufacturingDetails/supplier"):
            suppliers += [{
                "purchaseCost" : float(supplier.find("price").text) * dollars,
                "quantity" : int(supplier.find("quantity").text),
                "leadTime" : float(supplier.find("leadTime").text) * days}]
            
        if len(suppliers) > 0:
            setattr(loaded_part, "suppliers", suppliers)
            
        for coating in part.findall("manufacturingDetails/coatings/coating"):
            setattr(loaded_part, "coating", coating.text)
        
        make_process = Process(kind = "Make",
                               name = "Make " + loaded_part.name,
                               level = "activity",
                               part = loaded_part)
        
        loaded_parts[loaded_part.id] = loaded_part
        loaded_processes[loaded_part.id] = make_process
        
        LOGGER.info("Loaded part %s", loaded_part.name)
    
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
            for elem in ad.findall(".//*"):
                if elem.tag == "mechanical":
                    fastening_steps.append({ "method" : elem.find("fasteningMethod").text,
                                             "quantity" : int(elem.find("fasteningQuantity").text) })
                elif elem.tag in {"welding"}:
                    fastening_steps.append({ "method" : elem.tag })
            
        assemble_process = loaded_processes[subassembly.get("id")]
        assemble_process.set_predecessors(dependencies)
        setattr(assemble_process, "fasteningSteps", fastening_steps)
        
        LOGGER.info("Created assembly %s with dependencies %s", loaded_processes[subassembly.get("id")].name, dependencies)
    
    deliver = Process(kind = "Deliver",
                      name = "Deliver",
                      level = "activity",
                      predecessor = [p for p in loaded_processes.values() if len(p.successors) == 0])

    # Create the process graph
    processGraph = ProcessGraph(*loaded_processes.values(), deliver)
    return processGraph