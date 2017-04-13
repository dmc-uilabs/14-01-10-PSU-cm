from pml import *
import logging
import networkx as nx

'''For interactive console 
import os; import sys;os.chdir('C:/Users/kmh434/Documents/PML2/PML'); sys.path.append('C:/Users/kmh434/Documents/PML2/PML')
'''
#logging.basicConfig(level=logging.INFO)

# Initialize the system
auto_register("library")

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


#sg=graphsimulation(processGraph, simparam="cost", sdmultiplier=.2)    
# Save graph as image
#as_png(processGraph, "graph.png")



# Validate the graph by ensuring routings exist
if validate_graph(processGraph):
    print("Graph is valid!")
    #create a configuration object
    ourconfobj=getconfigparams(processGraph)
    committdb(ourconfobj)
    n=getparamsfromdb(2)
    print(ourconfobj.boxandwhiskercost)
    print(ourconfobj.boxandwhiskertime)
    print(ourconfobj.processcostrobustness)
    print(ourconfobj.processtimerobustness)
    print(ourconfobj.bestcostprocesses)
    print(ourconfobj.besttimeprocesses)
    print(ourconfobj.bestcost)
    print(ourconfobj.besttime)
        
#Configuration Analysis. 
#    Resources and resource analysis. 
#    Resources may not be static. Look into Resources. 
#    Make vs Buy. 
#    Vendors on the buy part. 

'''  
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(processGraph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
    
    print("-- Find shortest configuration --")
    (total_time, selected_processes) = find_min(processGraph, weight="time")
    print("    Shortest Configuration: %s" % as_time(total_time))

    print("-- Find heuristic configuration --")
    (lin_total, selected_processes) = find_min(processGraph, weight="linearcomb")
    print("    Cheapest Configuration: %s" % lin_total)

    # Save the minimum routings to a graph
    minimumGraph = create_subgraph(selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
     
else:
    print("Process graph is invalid - No routing exists")
    '''