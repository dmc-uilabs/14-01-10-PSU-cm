from pml import *
import logging
import networkx as nx
import pickle
import uuid
import struct
import sys
sys.setrecursionlimit(100000)

'''For interactive console 
import os; import sys;os.chdir('C:/Users/kmh434/Documents/PML2/PML'); sys.path.append('C:/Users/kmh434/Documents/PML2/PML')
'''
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
register_file("Assemble :: Bolting", "library/bolting.pml")

# Create an example two part assembly
weldment = []

for i in range(5):
    weldment.append(Part(name = "Bar " + str(i),
                length = 15 * inches,
                width = 1 * inch,
                height = 1 * inch,
                volume = 15 * inches**3,
                surface_area = 60 * inches**2,
                material = "Steel"))
    
engine = Part(name = "Engine",
             length = 3 * feet,
             width = 2 * feet,
             height = 3 * feet,
             purchaseCost = 1250 * dollars,
             volume = 18 * feet**3,
             surface_area = 16 * feet**2)

transmission = Part(name = "Transmission",
             length = 4 * feet,
             width = 2 * feet,
             height = 2 * feet,
             volume = 16 * feet**3,
             surface_area = 14 * feet**2,
             purchaseCost = 750 * dollars)

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
                                             "quantity" : 8 }])

mountPowertrainToChassis = Process(kind = "Assemble",
                               name = "Mount Engine/Transmission in Chassis",
                               level = "activity",
                               predecessor = [assemblePowertrain, assembleWeldment],
                               fasteningSteps = [{ "method" : "bolt",
                                                   "quantity" : 36 }])

deliver = Process(kind = "Deliver",
                  name = "Deliver",
                  level = "activity",
                   predecessor = mountPowertrainToChassis)

# Create and expand the process graph
processGraph = ProcessGraph(*activities, assembleWeldment, assemblePowertrain, mountPowertrainToChassis, deliver)
expand_graph(processGraph)


if validate_graph(processGraph):
    print("Graph is valid!")
    ''' first we pickle our processGraph object and store it in the local database as a binary blob of BYTEA'''
    ourpickledobject=pickleconfig(processGraph)
    '''Generate a UUID'''
    id=genuuid()
    '''This commits the binary object to the database with the uuid identifier'''
    committdbconfig(id,ourpickledobject)
    '''Here, we use a known uuid to query this database'''
    tempuuid='41ccf67e-6f31-4900-9b7e-305ffd794120'
    '''In this step, we pull the pickled object, unpickle it, and return the processGraph object'''
    unpickledprocessobject=getconfigfromdatabase(tempuuid)
    print(unpickledprocessobject) 
    '''here we show the object'''
    
    ''' 
    This next line is not trivial:
    1. We submit the process object and instantiate a class to hold the analysis data. This object looks like this,
        class ConfigurationObject:
         def __init__(self):
            self.config=None #placeholder
            self.boxandwhiskercost=None
            self.boxandwhiskertime=None
            self.processcostrobustness=None
            self.processtimerobustness=None
            self.bestcostprocesses=None
            self.besttimeprocesses=None
            self.bestcost=None
            self.besttime=None
    2. We generate various networks with different lognormal parameters and analyze the information.
        Calling as_networkx_sensitive from the analysis code provided to generate different configurations.
        When we get an as_networkx_sensitive object, we can call the getnodeperformance() function to analyze the robustness
        of each nodes across runs. This is stored in the processcostrobustness and processtimerobustness.
        The other variables are self-explanatory.
     '''    
    
    ourconfobj=getconfigparams(unpickledprocessobject)
    
    '''
    Here, we call a different library that instead connects to our analysis table to commit the analysis object.
    We commit the attributes to different fields in the table.  
    '''
    newuuid=genuuid()
    committdb(ourconfobj,newuuid)
    
    '''
    Now we pull from the database a row, and demonstrate how to grab stuff out of it. 
    '''
    
    n=getparamsfromdb(2) 
    print(ourconfobj.boxandwhiskercost)
    print(ourconfobj.boxandwhiskertime)
    print(ourconfobj.processcostrobustness)
    print(ourconfobj.processtimerobustness)
    print(ourconfobj.bestcostprocesses)
    print(ourconfobj.besttimeprocesses)
    print(ourconfobj.bestcost)
    print(ourconfobj.besttime)
    
    
    
    
    
    
    
    
    
    
    
    