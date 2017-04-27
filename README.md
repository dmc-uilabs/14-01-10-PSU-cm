# Process Model Library (PML) #

The Process Model Library (PML) is a Python library for modeling manufacturing
processes in a graph representation developed by The Pennsylvania State
University Applied Research Laboratory (PSU/ARL).  PML is based on prior work
on the DARPA Adaptive Vehicle Make (AVM) program, DMDII initiatives, and other
graph-like standards such as the Process Specification Language.

The PML programmatically generates process graphs using a Python-based
scripting language.  A process graph is a very generic graph data structure,
where nodes represent manufacturing processes and edges are dependencies between
processes.  A variety of graph search and analytic tools are subsequently used
to examine the process graph to find, for example, minimum cost routings or
maximum capacity (max flow).

The PML is designed to provide cost and lead time estimates at a conceptual
level.  It uses as input a high-level description of the part or assembly and
can quickly explore the tradeoffs between different manufacturing processes or
build quantities.

## PML Library ##

The `library` folder contains the default PML models.  PML models are Python
scripts that follow standard conventions for modifying the process graph.  The
process graph is a collection of processes and their dependencies.  A process
can contain arbitrary information, but at the minimum must have a defined 
`kind`.  Typically, we will include a name, level, and part information.

```python

    p1 = Process(kind = "Make :: Fabricate :: Investment Casting",
                 name = "Investment Casting",
                 level = "task",
                 part = parent.part)
```

The process graph is expanded in a recursive / hierarchical manner.  The
`kind` attribute is used to search the database for matching PML models.
The database is initialized by scanning the `library` folder for any
`__init__.pml` files.  Inside these initialization files, we register our
PML models:

```python

    register_file("Make :: Fabricate :: Investment Casting", "Investment Casting.pml")
```

Now, when we encounter the process from above, we execute the PML model
contained in `Investment Casting.pml`.  A PML model can perform a variety
of tasks.  Typically, this will involve performing any validation checks:

```python

    if not hasattr(parent.part, "material"):
        fail("Part has no defined material")
```

Looking up constants from the database:

```python

    laborCost = lookup_constant("Casting :: Labor Rate")
```

Providing cost and time estimates of various processes:

```python

    partVolume = parent.part.volume
    materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % material)
    meltingTime = (partVolume / inches**3) * lookup_constant("Casting :: Melting Time")
```

Constructing the processes that define this task:

```python

    p1 = Process(kind = "Make :: Fabricate :: Investment Casting :: Melting",
                 name = "Melting",
                 level = "operation",
                 time = meltingTime,
                 cost = laborCost * meltingTime + materialCost,
                 resource = ["Caster"])
```

And updating the process graph with our new processes:

```python

    replace(parent, p1)
```

You'll note that we referenced the `parent` several times.  Each PML model
is initialized with this global variable which points to the parent process.
This is used to pass information from the parent process to its child processes.

## Analysis ##

Constructing and analyzing a process graph works as follows.  First, we
initialize the database by loading the contents of the `library` folder and
load the input file.

```python

    auto_register("library")   
    processGraph = load_ebom(input_file)
```

Next, we expand the process graph using the PML models:
    
```python

    expand_graph(processGraph)
```

At this point, the process graph is generated and we can perform our analysis.
First, it is recommended to validate the graph.  This ensures that paths exists
between all nodes in the graph.

```python

    if validate_graph(processGraph):
        print("Graph is valid!")
```

If you're curious what the graph looks like, we can save it to an image.  This
requires GraphVis to be installed on your computer.

```python
    
    as_png(processGraph, "graph.png")
```

We can search the graph to find the minimum cost routings.

```python
    
    (cost, selected_processes) = find_min(processGraph, weight="cost")
```

The result is the minimum cost and the manufacturing processes that were
selected.  We can construct a new process graph with just these selected
processes and save it as an image:

```python
    
    minimumGraph = create_subgraph(processGraph, selected_processes)
    as_png(minimumGraph, "minimumGraph.png")
```


## DMC / DOME Integration ##

The file `dome.py` provides an interface to the Distributed Object Modeling
Environment (DOME) server, designed as a Name-Value Model.  The following inputs
are supported:

1. `inputFile` - XML representation of the part or assembly.  An example of
   an individual part is included below.  Note that this is designed to provide
   cost estimates using only high-level attributes (no geometry) that can be
   easily obtained from CAD software.


   ```xml
   
    <?xml version="1.0" encoding="UTF-8"?>
    <mBOM version="2.0">
        <parts>
            <part id="d1146573-70b3-4463-8fac-cd4fb59fa684">
                <name>Part1</name>
                <length unit="mm">47</length>
                <height unit="mm">50</height>
                <width unit="mm">47</width>
                <surface_area unit="mm2">13199</surface_area>
                <volume unit="mm3">42968</volume>
                <weight unit="kg">9.5</weight>
                <instances>
                    <instance instance_id="926d0684-20dc-4ce4-8ca3-52c2af4988cc" />
                </instances>
                <manufacturingDetails>
                    <material>Steel</material>
                    <coatings>
                        <coating>Powder Top Coating</coating>
                    </coatings>
                </manufacturingDetails>
            </part>
        </parts>
    </mBOM>
   
   ```

2. `userConstants` - Optional JSON file for overriding the default cost and
   time constants used by the PML models.  These constants are used to calibrate
   the models for a specific facility or locale.
   
   ```json
   
    [
        {
            "name" : "Casting :: Labor Rate",
            "value" : 60,
            "unit" : "dollars / hour"
        },
        {
            "name" : "Material :: Steel :: Cost",
            "value" : 0.5,
            "unit" : "dollars / inch**3"
        }
    ]
   ```
   
3. `optimizeWeight` - Optional parameter controlling how the optimal
   manufacturing routing is selected.  Valid inputs include `"cost"` and
   `"time"`.