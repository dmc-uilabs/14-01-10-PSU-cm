# painting can occur either on individual parts or on assemblies
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

generalLaborCost = lookup_constant("General Labor :: Labor Rate")
paintCost = lookup_constant("Material :: Paint :: Cost")
materialCost = surfaceArea * paintCost

cleanTime = (surfaceArea / inches**2) * 6 * seconds
applyTime = (surfaceArea / inches**2) * 3 * seconds
dryTime = 30 * minutes

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
			 
replace(parent, p1)