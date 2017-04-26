# estimate the surface area of the part or assembly
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

# lookup costs from the database
generalLaborCost = lookup_constant("Painting :: Labor Rate")
paintCost = lookup_constant("Material :: Powder :: Cost")

# estimate material cost from surface area
materialCost = surfaceArea * paintCost

# estimate painting times using surface area
washingTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Washing Time")
maskingTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Masking Time")
applyTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Apply Time")
curingTime = lookup_constant("Painting :: Curing Time")
dryingTime = lookup_constant("Painting :: Drying Time")

# create each of the operations
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
			
replace(parent, p1)