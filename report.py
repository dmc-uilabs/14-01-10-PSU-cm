#!/usr/bin/python3

from pml import *
import logging
import networkx as nx
from pylab import figure, axes, pie, title, show
import matplotlib
from matplotlib import pyplot as plt
import pdfkit


def gen_tradespace(alternatives, f='tradespace.png'):
    #print("    Alternatives:", pareto_alternatives)

    X = []
    Y = []
    labels = []

    for alt in pareto_alternatives:
        x = alt[1].args[0]/3600
        y = alt[0].args[0]
        X.append(x)
        Y.append(y)
        labels.append("$" + str(int(y)) + "\n" + str(int(x)) + " hours \n(" + str(int(x/24)) + " days)")


    #print (X)
    #print (Y)

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

    for label, x, y in zip(labels, X, Y):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-15, 15),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
        )



    plt.savefig(f)


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
as_png(process_graph, "graph.png")

# Validate the graph by ensuring routings exist
if validate_graph(process_graph):
    print()
      
    print("-- Find cheapest configuration --")
    (total_cost, selected_processes) = find_min(process_graph, weight="cost")
    print("    Cheapest Configuration: %s" % as_dollars(total_cost))
     
    print()
    print("-- Find quickest configuration --")
    (total_time, selected_processes) = find_min(process_graph, weight="time")
    print("    Quickest Configuration: %s" % as_time(total_time))
     
    print()
    print("-- Find best 50/50 configuration --")
    (cp_time, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
    print("    Best Configuration: %s" % as_time(str(cp_time)))
    (cp_cost, selected_processes) = find_min(process_graph, weight=lambda n : 0.5*n.cost/dollars + 0.5*n.time/days)
    print("    Best Configuration: %s" % as_dollars(str(cp_cost)))
    
    print()
    print("-- Saving configuration to PNG --")
    minimumGraph = create_subgraph(process_graph, selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
    
    print()
    print("-- Resources required by configuration --")
    print("   ", create_resources(selected_processes))

    print("-- Generating All Alternatives --")
    all_alternatives = generate_alternatives(process_graph, weights=("cost", "time"))
    gen_tradespace(all_alternatives)
    pareto_alternatives = pareto(all_alternatives)
    gen_tradespace(pareto_alternatives, 'pareto-alternatives.png')

    pdfkit.from_file('report-template.html', 'report.pdf')
      
else:
    print()
    print("Process graph is invalid - No routing exists")
    
