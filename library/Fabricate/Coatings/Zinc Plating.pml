# estimate the surface area of the part or assembly
if hasattr(parent, "part"):
	surfaceArea = parent.part.surface_area
elif hasattr(parent, "parts"):
	surfaceArea = sum([p.surface_area for p in parent.parts])
else:
	fail("Missing part or parts attributes")

# get plating labor cost
laborCost = lookup_constant("Plating :: Labor Rate")

# estimate plating times
setupTime = lookup_constant("Plating :: Setup Time")
strippingTime = (surfaceArea / inches**2) * lookup_constant("Plating :: Stripping Time")
blastingTime = (surfaceArea / inches**2) * lookup_constant("Plating :: Blasting Time")
platingTime = lookup_constant("Plating :: Plating Time")

# create the plating operations
p0 = Process(kind = "Make :: Fabricate :: Zinc Plating :: Setup",
			 name = "Setup",
			 level = "operation",
			 time = setupTime,
			 cost = laborCost * setupTime)
			 
p1 = Process(kind = "Make :: Fabricate :: Zinc Plating :: Stripping",
			 name = "Stripping",
			 level = "operation",
			 time = strippingTime,
			 cost = laborCost * strippingTime,
			 predecessor = p0)
			 
p2 = Process(kind = "Make :: Fabricate :: Zinc Plating :: Blasting and Grinding",
			 name = "Blasting and Grinding",
			 level = "operation",
			 time = blastingTime,
			 cost = laborCost * blastingTime,
			 predecessor = p1)
			 
p43 = Process(kind = "Make :: Fabricate :: Zinc Plating :: Copper Plating",
			 name = "Copper Plating",
			 level = "operation",
			 time = platingTime,
			 cost = laborCost * platingTime,
			 predecessor = p2)

p4 = Process(kind = "Make :: Fabricate :: Zinc Plating :: Zinc Plating",
			 name = "Zinc Plating",
			 level = "operation",
			 time = platingTime,
			 cost = laborCost * platingTime,
			 predecessor = p3)
		
replace(parent, p0)
