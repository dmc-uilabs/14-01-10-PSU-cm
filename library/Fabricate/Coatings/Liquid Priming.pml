# estimate the surface area of the part or assembly
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

# lookup costs from the database
laborCost = lookup_constant("Painting :: Labor Rate")
paintCost = lookup_constant("Material :: Paint :: Cost")

# estimate material cost from surface area
materialCost = surfaceArea * paintCost

# estimate painting times using surface area
maskingTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Masking Time")
applyTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Apply Time")
curingTime = lookup_constant("Painting :: Curing Time")
inspectingTime = lookup_constant("Painting :: Inspecting Time")
finishTime = lookup_constant("Painting :: Finishing Time")

# create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Masking",
			 name = "Masking",
			 level = "operation",
			 time = maskingTime,
			 cost = laborCost * maskingTime)
			 
p2 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Prime Coating",
			 name = "Prime Coating",
			 level = "operation",
			 predecessor = p1,
			 time = applyTime,
			 cost = laborCost * applyTime + materialCost)
			 
p3 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Curing",
			 name = "Curing",
			 level = "operation",
			 predecessor = p2,
			 time = curingTime,
			 cost = laborCost * curingTime)

p4 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Inspecting",
			 name = "Inspecting",
			 level = "operation",
			 predecessor = p3,
			 time = inspectingTime,
			 cost = laborCost * inspectingTime)

p5 = Process(kind = "Make :: Fabricate :: Liquid Priming :: Finish",
			 name = "Finish",
			 level = "operation",
			 predecessor = p4,
			 time = finishTime,
			 cost = laborCost * finishTime)
			
replace(parent, p1)