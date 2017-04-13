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

deburringTime = (surfaceArea / inches**2) * 6 * seconds
maskingTime = (surfaceArea / inches**2) * 6 * seconds
blastingTime = 30 * minutes
aircompressTime = 10 * minutes
degreasingTime = 20 * minutes

# Create each of the operations
p1 = Process(kind = "Make :: Fabricate :: Priming :: Deburring",
			 name = "Deburring",
			 level = "operation",
			 time = deburringTime,
			 cost = generalLaborCost * deburringTime)
			 
p2 = Process(kind = "Make :: Fabricate :: Priming :: Degreasing",
			 name = "Degreasing",
			 level = "operation",
			 predecessor = p1,
			 time = degreasingTime,
			 cost = generalLaborCost * degreasingTime)
			 
p3 = Process(kind = "Make :: Fabricate :: Priming :: Blast Masking",
			 name = "Blast Masking",
			 level = "operation",
			 predecessor = p2,
			 time = maskingTime,
			 cost = generalLaborCost * maskingTime)

p4 = Process(kind = "Make :: Fabricate :: Priming :: Abrasive Blasting",
			 name = "Abrasive Blasting",
			 level = "operation",
			 predecessor = p3,
			 time = blastingTime,
			 cost = generalLaborCost * blastingTime)

p5 = Process(kind = "Make :: Fabricate :: Priming :: Air Compress",
			 name = "Air Compress",
			 level = "operation",
			 predecessor = p4,
			 time = aircompressTime,
			 cost = generalLaborCost * aircompressTime)

			
# Finally, link the parent (in this case, the Priming task) to the
# operation chain starting at p1. 
replace(parent, p1)