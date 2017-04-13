# Painting can occur either on individual parts or on assemblies.
# Here, we estimate the painting cost by using the surface area.
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

# Lookup constants from the database
generalLaborCost = lookup_constant("General Labor :: Labor Rate")
paintCost = lookup_constant("Material :: Paint :: Cost")

# Estimate the costs and times
materialCost = surfaceArea * paintCost

cleanTime = (surfaceArea / inches**2) * 6 * seconds
applyTime = (surfaceArea / inches**2) * 3 * seconds
dryTime = 30 * minutes

# Create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Paint :: Clean",
			 name = "Clean",
			 level = "operation",
			 time = cleanTime,
			 cost = generalLaborCost * cleanTime)
			 
p2 = Process(kind = "Make :: Fabricate :: Paint :: Apply Coat",
			 name = "Apply Coat",
			 level = "operation",
			 predecessor = p1,
			 time = applyTime,
			 cost = generalLaborCost * applyTime + materialCost)
			 
p3 = Process(kind = "Make :: Fabricate :: Paint :: Dry",
			 name = "Dry",
			 level = "operation",
			 predecessor = p2,
			 time = dryTime,
			 cost = 0 * dollars)
			
# Finally, link the parent (in this case, the Paint task) to the
# operation chain starting at p1. 
replace(parent, p1)