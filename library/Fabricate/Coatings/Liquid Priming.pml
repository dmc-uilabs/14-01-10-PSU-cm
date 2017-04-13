# Priming can occur either on individual parts or on assemblies.
# Here, we estimate the priming cost by using the surface area.
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

maskingTime = (surfaceArea / inches**2) * 6 * seconds
applyTime = (surfaceArea / inches**2) * 3 * seconds
curingTime = 30 * minutes
inspectingTime = 10 * minutes
finishTime = 30 * minutes

# Create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Masking",
			 name = "Masking",
			 level = "operation",
			 time = maskingTime,
			 cost = generalLaborCost * maskingTime)
			 
p2 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Prime Coating",
			 name = "Prime Coating",
			 level = "operation",
			 predecessor = p1,
			 time = applyTime,
			 cost = generalLaborCost * applyTime + materialCost)
			 
p3 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Curing",
			 name = "Curing",
			 level = "operation",
			 predecessor = p2,
			 time = curingTime,
			 cost = generalLaborCost * curingTime)

p4 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Inspecting",
			 name = "Inspecting",
			 level = "operation",
			 predecessor = p3,
			 time = inspectingTime,
			 cost = generalLaborCost * inspectingTime)

p5 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Finish",
			 name = "Finish",
			 level = "operation",
			 predecessor = p4,
			 time = finishTime,
			 cost = generalLaborCost * finishTime)
			
# Finally, link the parent (in this case, the Liquid Priming task) to the
# operation chain starting at p1. 
replace(parent, p1)