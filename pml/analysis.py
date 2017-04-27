import networkx as nx
from .units import *
from .model import *
from .convert import *
import numpy
import re
import pickle 
import uuid
from collections import defaultdict


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

def connectdb():
    import psycopg2    
    try:
        conn=psycopg2.connect("dbname='AnalysisReports' user='postgres' password='kmh434'")
    except:
        print("I am unable to connect to the database.")
    curs=conn.cursor()
    return curs, conn

def closedb(curs, conn):
    curs.close()
    conn.close()
    return

def getparamsfromdb(idnum):
    i,j=connectdb()
    i.execute("SELECT * from pmlanalysis WHERE ident=(%s);", (idnum,))
    dbvals=i.fetchone()
    newconfigobject=ConfigurationObject
    newconfigobject.config=dbvals[1] #placeholder
    newconfigobject.boxandwhiskercost=dbvals[2]
    newconfigobject.boxandwhiskertime=dbvals[3]
    newconfigobject.processcostrobustness=dbvals[4]
    newconfigobject.processtimerobustness=dbvals[5]
    newconfigobject.bestcostprocesses=dbvals[6]
    newconfigobject.besttimeprocesses=dbvals[7]
    newconfigobject.bestcost=dbvals[8]
    newconfigobject.besttime=dbvals[9]
    #closedb(i,j)
    return newconfigobject

def committdb(configobject,id):
    import psycopg2    
    try:
        conn=psycopg2.connect("dbname='AnalysisReports' user='postgres' password='kmh434'")
    except:
        print("I am unable to connect to the database.")
    curs=conn.cursor()
    curs.execute("INSERT INTO pmlanalysis (config, boxandwhiskercost, boxandwhiskertime, processcostrobustness, processtimerobustness, bestcostprocesses, besttimeprocesses, bestcost, besttime)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (str(id),
        str(configobject.boxandwhiskercost), 
        str(configobject.boxandwhiskertime), 
        str(configobject.processcostrobustness), 
        str(configobject.processtimerobustness), 
        str(configobject.bestcostprocesses),
        str(configobject.besttimeprocesses),
        str(configobject.bestcost),
        str(configobject.besttime)))
    curs.execute("SELECT * from pmlanalysis;")
    #print(curs.fetchall())
    conn.commit()
    curs.close()
    conn.close()
    return
    
def getconfigparams(processGraph):   
    Thisconfig=ConfigurationObject()
    #a=as_networkx_sensitive(processGraph, weight="time")
    timeperf=getnodeperformance(as_networkx_sensitive(processGraph, weight="time"))
    costperf=getnodeperformance(as_networkx_sensitive(processGraph, weight="cost"))
    (total_cost, selected_processes) = find_min_simvar(processGraph, weight="cost",simvar=1000)
    (total_time, selected_processes2) = find_min_simvar(processGraph, weight="time",simvar=1000)
    (nom_cost, a) = find_min_simvar(processGraph, weight="cost",simvar=1)
    (nom_time, b) = find_min_simvar(processGraph, weight="time",simvar=1)
    Thisconfig.boxandwhiskercost=as_dollars(total_cost)
    Thisconfig.boxandwhiskertime=as_time(total_time)
    Thisconfig.processcostrobustness=costperf
    Thisconfig.processtimerobustness=timeperf
    Thisconfig.bestcostprocesses=selected_processes
    Thisconfig.besttimeprocesses=selected_processes2
    Thisconfig.bestcost=nom_cost
    Thisconfig.besttime=nom_time    
    return Thisconfig

def find_min_monte(graph, weight = None, networkx = None, reps=None):
    from collections import defaultdict
    contributions_dict=defaultdict()
    for i in range(len(reps)):
        total = 0
        selected_processes = set()
        if weight is None:
            weight = "cost"
        if networkx is None:
            for curvar in list(range(1,1100,100)):
                networkx = as_networkx_simvar(graph, weight = weight, simvar=curvar)
                for n in networkx.nodes():
                    weights=getattr(n,weight) if hasattr(n,weight) else 0
                    contributions_dict[n].append(weights)
    return (contributions_dict)
    
def preproc(thing, sd, wtype):
    #we should not need this:
     #print(thing)
     if str(thing)[0]=="/":
        thing="1"+ str(thing)
     if wtype=="cost":
        floatval= numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(thing)))), sd, 1)))[0] if (numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(thing)))), sd, 1)))[0]) and numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(thing)))), sd, 1)))[0]))==False else 0
     if wtype=="time":
        floatval=numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[s* ]', '', str(thing)))), sd, 1)))[0] if numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[s* ]', '', str(thing)))), sd, 1)))[0])==False else 0
     if wtype=="linearcomb":
         thing= ygetattr(node,"cost") if hasattr(node,"cost") else 0
         tempcproc= numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(thing)))), sd, 1)))[0] if numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(thing)))), sd, 1)))[0])==False else 0
     
         thing=getattr(node,"time") if hasattr(node,"time") else 0
         temptproc=numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[s* ]', '', str(thing)))), sd, 1)))[0] if numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[s* ]', '', str(thing)))), sd, 1)))[0])==False else 0
         floatval=.5*tempcproc + .5*temptproc
     return floatval
 

def safe_log(x):
    if x <= 0:
        return 0
    if numpy.isinf(numpy.log(x)):
        return 0
    return numpy.log(x)[0]


def preprocv2(thing, sd, wtype):
    #we should not need this:
     stringthing=str(thing)
     if len(stringthing)==0:
         return 0
     if len(stringthing)>0:
         stringthing.replace('-','')
        
     if wtype=="cost":
        if len(stringthing)>1:
            if stringthing[1]=="/":
                stringthing='1'+ stringthing

        trimstr = str(re.sub('[!@#$*]', '',stringthing))
        
        if len(trimstr) == 0:
            trimstr = "1"
        
        floatval= numpy.abs(safe_log(numpy.random.lognormal(eval(trimstr), sd, 1)))
        #print(floatval)
        return floatval        
        
     if wtype=="time":
        if len(stringthing)>1:
            if stringthing[1]=="/":
                stringthing='1'+ stringthing
                
        trimstr = str(re.sub('[s* ]', '', stringthing))
        
        if len(trimstr) == 0:
            trimstr = "1"
                
        floatval=numpy.abs(safe_log(numpy.random.lognormal(eval(trimstr), sd, 1)))
        #print(floatval)
        return floatval       
 
def as_networkx_sensitive(graph, weight="cost", simvarrange=[1,10000,25]):
    from collections import defaultdict
    processes = graph.processes
    graph = nx.DiGraph()
    
    if not hasattr(processes, "__iter__"):
        processes = [processes]
    
    # first create the nodes
    unprocessed = set()
    unprocessed.update(processes)
    processed = set()
    
    counter = 0
    id_map = {}
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        counter += 1
        
        #print("Adding node " + pick.name + " with id " + str(counter))
        id_map[pick] = str(counter)
        graph.add_node(pick)
        processed.add(pick)
        
        for successor in pick.successors:            
            if successor not in processed:
                unprocessed.add(successor)
    thedict=defaultdict(list)            
    for simvar in list(range(simvarrange[0],simvarrange[1],simvarrange[2])):            
        for node in processed:
            for successor in node.successors:
                if weight=="linearcomb":
                    wv1=getattr(node,"cost") if hasattr(node,"cost") else 0; wv2=getattr(node,"time") if hasattr(node,"time") else 0
                    weight_value=.5*(preprocv2(wv1,simvar,"cost"))+.5*(preprocv2(wv2,simvar,"time"))
                if weight=="cost":
                    tw = getattr(node, "cost") if hasattr(node, "cost") else 0
                    weight_value=preprocv2(tw, simvar, "cost")
                   # print("Adding edge between " + node.name + " and " + successor.name + " with weight " + str(weight_value))
                if weight=="time":
                    tw = getattr(node, "time") if hasattr(node, "time") else 0
                    weight_value=preprocv2(tw, simvar, "time") 
                   # print("Adding edge between " + node.name + " and " + successor.name + " with weight " + str(weight_value))

                thedict[node].append(weight_value)        
            #print(weight_value)
           
            
    return thedict

def generatetopography(processGraph):
    simgraph=as_networkx_simvar(processGraph)
    bigM=1000000
    milemarkers=list(filter(lambda thenode: thenode.level=="activity",simgraph.nodes()))
    topography={}
    for currentmile in milemarkers:
        distlist=[]
        for mile in milemarkers:
            try:
                 distlist.append(len(nx.shortest_path(simgraph, source=currentmile, target=mile)))
            except:
                donothing=1
                try:
                    distlist.append(len(nx.shortest_path(simgraph, source=mile, target=currentmile)))
                except:
                    donothing=1
                    pass
            finally:
                distlist.append(1000000) 
        print(milemarkers)
        print(numpy.argmin(distlist))
        topography[currentmile]=milemarkers[numpy.argmin(distlist)]
        
    return simgraph, topography  
'''
This should not be needed, but there is a bug in the cost code that allows for strange things, like a cost of /2$
'''
def cleangraph(graph):
    for node in graph.nodes():
        if hasattr(node,"cost") and str(node.cost)=="$/2":
            node.cost="$1/2"
    return(graph)
        
def graphsimulation(processGraph, simparam="cost", sdmultiplier=1):
    import re
    simgraph=as_networkx_simvar(processGraph) 
    simgraph=cleangraph(simgraph) #get the graph
    for node in simgraph.nodes():
       #print(node.cost) if hasattr(node,"cost") else 0
       if simparam=="cost" and hasattr(node,"cost")==True:            
         node.cost=numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(node.cost)))), sdmultiplier, 1)))[0] if numpy.isinf(numpy.abs(numpy.log(numpy.random.lognormal(eval(str(re.sub('[!@#$*]', '', str(node.cost)))), sdmultiplier, 1)))[0])==False else 0
       if simparam=="cost" and hasattr(node, "cost")==False:
           node.cost=0      
    return simgraph

def find_min_simvar(graph, weight = None, networkx = None, simvar=None):
    total = 0
    selected_processes = set()
    
    if weight is None:
        weight = "cost"
    
    if networkx is None:
        networkx = as_networkx_simvar(graph, weight = weight, simvar=simvar)
    
    for original_process in graph.original_processes.keys():
        new_process = graph.original_processes[original_process]
        
        for original_successor in original_process.successors:
            new_successor = graph.original_processes[original_successor]
            path = nx.shortest_path(networkx, new_process, new_successor, weight = weight)
            
            selected_processes.update(path)
            total += sum([getattr(p, weight) if hasattr(p, weight) else 0 for p in path])
                
    return (total, selected_processes)

def as_networkx_simvar(graph, weight="cost",simvar=1):
    processes = graph.processes
    graph = nx.DiGraph()
    
    if not hasattr(processes, "__iter__"):
        processes = [processes]
    
    # first create the nodes
    unprocessed = set()
    unprocessed.update(processes)
    processed = set()
    
    counter = 0
    id_map = {}
    
    while len(unprocessed) > 0:
        pick = unprocessed.pop()
        counter += 1
        
        id_map[pick] = str(counter)
        graph.add_node(pick)
        processed.add(pick)
        
        for successor in pick.successors:            
            if successor not in processed:
                unprocessed.add(successor)
                
    for node in processed:
        for successor in node.successors:
            weight_value = getattr(node, weight) if hasattr(node, weight) else 0
            graph.add_edge(node, successor, **{weight : weight_value})
            
    return graph 

def pickleconfig(processGraph):
    return pickle.dumps(processGraph)

def committdbconfig(id,pickledobject):
    import psycopg2    
    try:
        conn=psycopg2.connect("dbname='AnalysisReports' user='postgres' password='kmh434'")
    except:
        print("I am unable to connect to the database.")
    curs=conn.cursor()
    curs.execute("INSERT INTO configurationstest (uuid, pickledconfig)  VALUES (%s, %s)",
        (genuuid(),
        psycopg2.Binary(pickledobject), 
        ))
    curs.execute("SELECT * from configurationstest;")
    #print(curs.fetchall())
    conn.commit()
    curs.close()
    conn.close()
    return 

def getconfigfromdatabase(uuidval):
    import psycopg2    
    try:
        conn=psycopg2.connect("dbname='AnalysisReports' user='postgres' password='kmh434'")
    except:
        print("I am unable to connect to the database.")
    curs=conn.cursor()
    curs.execute("SELECT * from configurationstest WHERE uuid = (%s)", (uuidval,))
    whatwegot=curs.fetchone()
    print(whatwegot[0])
    grobj=pickle.loads(whatwegot[1])
    curs.close()
    conn.close()
    return grobj

def genuuid():
    return(str(uuid.uuid4()))
    
def getnodeperformance(networkx_sensitive_object):
    perfdict={}
    bigm=1000000
    for n in networkx_sensitive_object.keys():
        curval=networkx_sensitive_object[n]
        if max(curval) > 0:
            vec=curval/max(networkx_sensitive_object[n])
            perfdict[n]=numpy.var(vec)
        else:
            perfdict[n]=bigm    
    return perfdict