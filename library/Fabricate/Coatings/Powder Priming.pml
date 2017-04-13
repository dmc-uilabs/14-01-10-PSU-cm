# Priming can occur either on individual parts or on assemblies.
# Here, we estimate the priming cost by using the surface area.
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

# Lookup constants from the database
generalLaborCost = lookup_constant("Painter :: Labor Rate")
paintCost = lookup_constant("Material :: Paint :: Cost")

# Estimate the costs and times
materialCost = surfaceArea * paintCost

washingTime = (surfaceArea / inches**2) * 6 * seconds
maskingTime = (surfaceArea / inches**2) * 6 * seconds
applyTime = (surfaceArea / inches**2) * 3 * seconds
curingTime = 30 * minutes
dryingTime = 60 * minutes

# Create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Powder Priming :: Pre-Treat Washing",
			 name = "Pre-Treat Washing",
			 level = "operation",
			 time = washingTime,
			 cost = generalLaborCost * washingTime,
			 resource = "Painter")
			 
p2 = Process(kind = "Make :: Fabricate :: Powder Prime :: Drying",
			 name = "Drying",
			 level = "operation",
			 predecessor = p1,
			 time = dryingTime,
			 cost = generalLaborCost * dryingTime + materialCost,
			 resource = "Painter")
			 
p3 = Process(kind = "Make :: Fabricate :: Powder Prime :: Apply",
			 name = "Apply",
			 level = "operation",
			 predecessor = p2,
			 time = applyTime,
			 cost = generalLaborCost * applyTime,
			 resource = "Painter")

p4 = Process(kind = "Make :: Fabricate :: Powder Prime :: Curing",
			 name = "Curing",
			 level = "operation",
			 predecessor = p3,
			 time = curingTime,
			 cost = generalLaborCost * curingTime,
			 resource = "Painter")

p5 = Process(kind = "Make :: Fabricate :: Powder Prime :: Apply",
			 name = "Apply",
			 level = "operation",
			 predecessor = p4,
			 time = applyTime,
			 cost = generalLaborCost * applyTime,
			 resource = "Painter")

p6 = Process(kind = "Make :: Fabricate :: Powder Prime :: Masking",
			 name = "Masking",
			 level = "operation",
			 predecessor = p5,
			 time = maskingTime,
			 cost = generalLaborCost * maskingTime,
			 resource = "Painter")
			
# Finally, link the parent (in this case, the Powder Priming task) to the
# operation chain starting at p1. 
replace(parent, p1)