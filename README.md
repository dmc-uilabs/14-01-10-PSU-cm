Process Model Library (PML)
===========================

The Process Model Library (PML) is an attempt to reenvision the mechanism for representing
and processing processes models.  Based on prior work on the DARPA Adaptive Vehicle Make (AVM)
program, DMDII initiatives, and other open standards such as the Process Specification Language,
the PML seeks to provide a standards-driven representation for programmatically generating
process graphs.

PML is primarily composed of two modules: the process graph and the process modeling language.
The process graph is a generic graph representation with nodes and edges.  Each node represents
a specific process, and we use process very generically so that they could represent manufacturing,
engineering, or business processes, for example.  Edges represent the dependencies between processes,
which could more concretely represent the flow of information or material through the process graph.

The process modeling language provides an iterative, programmatic mechanism for generating the graph.
The mechanism begins by "seeding" one or more initial nodes.  Each node requires a "kind" attribute,
which is used to locate the appropriate process model (or models if more than one feasible model
exists).  The process model is then executed to "expand" the original node with finer details, typically
by adding additional nodes and edges to the graph.  This iterative process continues until no further
expansion is possible.

After the process graph is generated, it can also undergo various "filters".  Filters are intended to 
reduce a complex, detailed process graph into a smaller, more concise, and efficient representation
for a particular analysis.