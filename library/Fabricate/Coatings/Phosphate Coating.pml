laborCost = lookup_constant("Plater :: Labor Rate")
setupTime = 5 * minutes
preparationTime = 15 * minutes
cleaningTime = 10 * minutes
activationTime = 20 * minutes
phosphatingTime = 60 * minutes
treatmentTime = 20 * minutes

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
