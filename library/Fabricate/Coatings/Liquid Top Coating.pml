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
applyTime = (surfaceArea / inches**2) * lookup_constant("Painting :: Apply Time")
curingTime = lookup_constant("Painting :: Curing Time")
inspectingTime = lookup_constant("Painting :: Inspecting Time")

# create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Apply Paint",
			 name = "Apply Paint",
			 level = "operation",
			 time = applyTime,
			 cost = laborCost * applyTime + materialCost)
			 
p2 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Curing",
			 name = "Curing",
			 level = "operation",
			 predecessor = p1,
			 time = curingTime,
			 cost = laborCost * curingTime)

p3 = Process(kind = "Make :: Fabricate :: Liquid Top Coating :: Inspecting",
			 name = "Inspecting",
			 level = "operation",
			 predecessor = p2,
			 time = inspectingTime,
			 cost = laborCost * inspectingTime)

replace(parent, p2)