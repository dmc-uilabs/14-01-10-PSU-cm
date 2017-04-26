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
preparationTime = lookup_constant("Plating :: Phosphate Coating :: Preparation Time")
cleaningTime = lookup_constant("Plating :: Phosphate Coating :: Cleaning Time")
activationTime = lookup_constant("Plating :: Phosphate Coating :: Activation Time")
phosphatingTime = lookup_constant("Plating :: Phosphate Coating :: Phosphating Time")
treatmentTime = lookup_constant("Plating :: Phosphate Coating :: Treatment Time")

# create the plating operations
p1 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Setup",
			 name = "Setup",
			 level = "operation",
			 time = setupTime,
			 cost = laborCost * setupTime)
			 
p2 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Prepare Surface",
			 name = "Prepare Surface",
			 level = "operation",
			 time = preparationTime,
			 cost = laborCost * preparationTime,
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Clean Part",
			 name = "Clean Part",
			 level = "operation",
			 time = cleaningTime,
			 cost = laborCost * cleaningTime,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Activation/Conditioning",
			 name = "Activation/Conditioning",
			 level = "operation",
			 time = activationTime,
			 cost = laborCost * activationTime,
			 predecessor = p3)

p5 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Phosphating",
			 name = "Phosphating",
			 level = "operation",
			 time = phosphatingTime,
			 cost = laborCost * phosphatingTime,
			 predecessor = p4)

p6 = Process(kind = "Make :: Fabricate :: Phosphate Coating :: Post Phosphating Treatment",
			 name = "Post Phosphating Treament",
			 level = "operation",
			 time = treatmentTime,
			 cost = laborCost * treatmentTime,
			 predecessor = p5)
		
replace(parent, p1)