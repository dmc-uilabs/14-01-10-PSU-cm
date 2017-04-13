laborCost = lookup_constant("Plater :: Labor Rate")
setupTime = 5 * minutes
strippingTime = 30 * minutes
blastingTime = 20 * minutes
platingTime = 60 * minutes

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
