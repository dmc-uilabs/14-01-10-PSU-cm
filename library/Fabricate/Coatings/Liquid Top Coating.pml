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

applyTime = (surfaceArea / inches**2) * 3 * seconds
curingTime = 30 * minutes
inspectingTime = 10 * minutes

# Create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Apply Paint",
			 name = "Apply Paint",
			 level = "operation",
			 time = applyTime,
			 cost = generalLaborCost * applyTime + materialCost)
			 
p2 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Curing",
			 name = "Curing",
			 level = "operation",
			 predecessor = p1,
			 time = curingTime,
			 cost = generalLaborCost * curingTime)

p3 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Inspecting",
			 name = "Inspecting",
			 level = "operation",
			 predecessor = p2,
			 time = inspectingTime,
			 cost = generalLaborCost * inspectingTime)

			
# Finally, link the parent (in this case, the Liquid Top Coating task) to the
# operation chain starting at p1. 
replace(parent, p2)