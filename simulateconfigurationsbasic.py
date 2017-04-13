from pml import *
import logging
import networkx as nx
import numpy
import sys
sys.setrecursionlimit(100000)

# This loads all PML files in the library/ folder and also initializes the constants.
auto_register("library")

for replication in range(25):
    # Override the constants
    set_constant("Machinist :: Labor Rate", numpy.random.poisson(59) * dollars / hour)
    set_constant("Caster :: Labor Rate", numpy.random.poisson(30) * dollars / hour)
    set_constant("General Labor :: Labor Rate", numpy.random.poisson(25) * dollars / hour)
    set_constant("Welder :: Labor Rate", numpy.random.poisson(40) * dollars / hour)
    set_constant("X-Ray Machine :: Cost", numpy.random.poisson(10) * dollars)
    set_constant("Material :: Steel :: Cost", numpy.random.poisson(0.5) * dollars / inch**3)
    set_constant("Material :: Aluminum :: Cost", numpy.random.poisson(0.8) * dollars / inch**3)
    set_constant("Material :: Paint :: Cost", numpy.random.poisson(0.2) * dollars / inch**2)
    
    # Create an example two part assembly
    weldment = []
    
    for i in range(5):
        weldment.append(Part(name = "Bar " + str(i),
                    length = numpy.random.poisson(15) * inches,
                    width = numpy.random.poisson(1) * inch,
                    height = numpy.random.poisson(1) * inch,
                    volume = numpy.random.poisson(15) * inches**3,
                    surface_area = numpy.random.poisson(60) * inches**2,
                    material = "Steel"))
        
    engine = Part(name = "Engine",
                 length = numpy.random.poisson(3) * feet,
                 width = numpy.random.poisson(2) * feet,
                 height = numpy.random.poisson(3) * feet,
                 purchaseCost = numpy.random.poisson(1250) * dollars,
                 volume = numpy.random.poisson(18) * feet**3,
                 surface_area = numpy.random.poisson(16) * feet**2)
    
    transmission = Part(name = "Transmission",
                 length = numpy.random.poisson(4) * feet,
                 width = numpy.random.poisson(2) * feet,
                 height = numpy.random.poisson(2) * feet,
                 volume = numpy.random.poisson(16) * feet**3,
                 surface_area = numpy.random.poisson(14) * feet**2,
                 purchaseCost = numpy.random.poisson(750) * dollars)
    
    activities = []
    
    for part in [*weldment, engine, transmission]:
        activities.append(Process(kind = "Make",
                                  name = "Make " + part.name,
                                  level = "activity",
                                  part = part))
        
    assembleWeldment = Process(kind = "Assemble",
                               name = "Assemble Weldment",
                               level = "activity",
                               predecessor = [a for a in activities if a.part in weldment],
                               fasteningSteps = [{ "method" : "weld",
                                                   "weldLength" : 2 * (a.part.width + a.part.height)} for a in activities if a.part in weldment])
    
    assemblePowertrain = Process(kind = "Assemble",
                             name = "Mount Transmission to Engine",
                             level = "activity",
                             predecessor = [a for a in activities if a.part not in weldment],
                             fasteningSteps = [{ "method" : "bolt",
                                                 "quantity" : numpy.random.poisson(8) }])
    
    mountPowertrainToChassis = Process(kind = "Assemble",
                                   name = "Mount Engine/Transmission in Chassis",
                                   level = "activity",
                                   predecessor = [assemblePowertrain, assembleWeldment],
                                   fasteningSteps = [{ "method" : "bolt",
                                                       "quantity" : numpy.random.poisson(36) }])
    
    deliver = Process(kind = "Deliver",
                      name = "Deliver",
                      level = "activity",
                       predecessor = mountPowertrainToChassis)
    
    # Create and expand the process graph
    processGraph = ProcessGraph(*activities, assembleWeldment, assemblePowertrain, mountPowertrainToChassis, deliver)
    expand_graph(processGraph)

    if validate_graph(processGraph):
        print("valid graph")
        print(replication)
        ourpickledobject=pickleconfig(processGraph)
        
        current_id=genuuid()
        
        committdbconfig(current_id, ourpickledobject)
    
        ourconfobj=getconfigparams(processGraph)
    
        committdb(ourconfobj, current_id)
        print("we got it")
    
    
