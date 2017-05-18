#!/usr/bin/python3

from pml import *
import logging
import networkx as nx
from pylab import figure, axes, pie, title, show
import matplotlib
from matplotlib import pyplot as plt
import pdfkit

AUTH_TOKEN=False

def print_alternatives(alternatives):
    for i, pa in enumerate(alternatives):
        print("    Alternative %d:" % i)
        print("        Cost:", as_dollars(pa["cost"]))
        print("        Time:", as_time(pa["time"]))
        print("        Processes:", pa["selected_processes"])
        print("        Graph: Saved to alternative%d.png" % i)
        as_png(pa["process_graph"], "alternative%d.png" % i)



def gen_tradespace(alternatives, f='tradespace.png', annotate=True):
    X = []
    Y = []
    labels = []

    for alt in alternatives:
        #print (str(alt))
        x = alt['time'].args[0]/3600
        y = alt['cost'].args[0]
        #print (str(x))
        #print (str(y))
        X.append(x)
        Y.append(y)
        #print ("\n\n\n HIIII \n\n\n")
        #print (str(X))
        labels.append("$" + str(int(y)) + "\n" + str(int(x)) + " hours \n(" + str(int(x/24)) + " days)")


    #print (str(X))
    #print (str(Y))
    #print (str(labels))

    plt.xlabel("Time (hours)")
    plt.ylabel("Cost (USD $)")


    plt.scatter(X,Y, marker='o', c='lightblue', s=50, cmap=plt.get_cmap('Spectral'))

#    ax = plt.subplot(111,aspect = 'equal')
#    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

#    plot_margin = 0.55

#    x0, x1, y0, y1 = plt.axis()
#    plt.axis((x0 - plot_margin,
#            x1 + plot_margin,
#            y0 - plot_margin,
#            y1 + plot_margin))

# JAB reserves the right to fiddle around with the colors at a later time ;)
#    fig = plt.figure()
#    fig.patch.set_facecolor('black')
#    ax = plt.subplot()
#    ax.set_facecolor('black')

    if (True==annotate):
        for label, x, y in zip(labels, X, Y):
            plt.annotate(
                label,
                xy=(x, y), xytext=(-15, 15),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
            )



    plt.savefig(f)




def validate_auth(auth_token):
    return False
    #return True)


def err_out(message):
    #read error-template-pt1.html
    file = open('report-templates/error-template-pt1.html', 'r')
    final_html = file.read()
    final_html = final_html + "<h1>" + message + "~</h1>\n"
    file.close
    file = open('report-templates/error-template-pt2.html', 'r')
    final_html = final_html + file.read()
    file.close

    file = open('report-templates/error-template.html', 'w')
    file.write(final_html)
    file.flush()
    file.close
    
    pdfkit.from_file('report-templates/error-template.html', 'report.pdf')
    #pdfkit.from_file('report-templates/error-template.working.html', 'report.pdf')
    quit()

if (False==validate_auth(AUTH_TOKEN)):
    err_out("Invalid Authorization - no report generated")


# Scan the library/ folder and its subfolders for __init__.pml files, which are
# executed to initialize the PML "database"
auto_register("library")

# Load the eBOM.xml file
path = r"examples/engine_assembly"
file = os.path.join(path, "eBOM.xml")
file = r"examples/simpleExample.xml"

process_graph = load_ebom(file, build_quantity=50)

# Expand the process graph using the PML models
expand_graph(process_graph)

# # Save graph as image
as_png(process_graph, "full-graph.png")

# Validate the graph by ensuring routings exist
if validate_graph(process_graph):
    #print()
      
    #print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(process_graph, weight="cost")
    #print("    Cheapest Configuration: %s" % as_dollars(total_cost))
    minimumGraph = create_subgraph(process_graph, selected_processes)
    as_png(minimumGraph, "cheapestGraph.png")
     
    #print()
    #print("-- Find quickest configuration --")
    (total_time, selected_processes) = find_min(process_graph, weight="time")
    #print("    Quickest Configuration: %s" % as_time(total_time))
    minimumGraph = create_subgraph(process_graph, selected_processes)
    as_png(minimumGraph, "fastestGraph.png")
     
    #print()
    #print("-- Find best 50/50 configuration --")
    (cp_time, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
    #print("    Best Configuration: %s" % as_time(str(cp_time)))
    (cp_cost, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
    #print("    Best Configuration: %s" % as_dollars(str(cp_cost)))
    minimumGraph = create_subgraph(process_graph, selected_processes)
    as_png(minimumGraph, "balancedGraph.png")
    
    #print()
    #print("-- Saving configuration to PNG --")
    #minimumGraph = create_subgraph(process_graph, selected_processes)
    #as_png(minimumGraph, "minimumGraph.png")
    
    #print()
    #print("-- Resources required by configuration --")
    #print("   ", create_resources(selected_processes))

    #print ("\n\n\n---ALLLL----\n\n\n")
    all_alternatives = generate_alternatives(process_graph, weights=("cost", "time"))
    #print_alternatives(all_alternatives)
    gen_tradespace(all_alternatives, 'all-alternatives', annotate=False)

    #print ("\n\n\n---PAAARRREEETTTOOOOSSSS----\n\n\n")
    all_alternatives = generate_alternatives(process_graph, weights=("cost", "time"))
    pareto_alternatives = pareto(all_alternatives, weights=("cost", "time"))
    #print_alternatives(pareto_alternatives)
    gen_tradespace(pareto_alternatives, 'pareto-alternatives.png')

    #manufacturability feedback
    #for feedback in MFG_FEEDBACK:
        #print (str(feedback))

    pdfkit.from_file('report-template.html', 'report.pdf')
      
else:
    err_out("Not manufacturable with this production center - no report generated")
    #print()
    #print("Process graph is invalid - No routing exists")
    
