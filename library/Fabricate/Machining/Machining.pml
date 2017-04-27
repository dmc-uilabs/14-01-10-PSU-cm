# If the part does not have a material, it can not be machined
if not hasattr(parent.part, "material"):
	fail("Part has no defined material")
	
if not hasattr(parent.part, "quantity"):
	fail("Part has no defined quantity")

# We will estimate the cost based on the removal volume
stockVolume = parent.part.length * parent.part.width * parent.part.height
partVolume = parent.part.volume
removalVolume = stockVolume - partVolume

# Lookup the machinist labor rate from the database
machinistCost = lookup_constant("Machining :: Labor Rate")

# Estimate the material cost
materialCost = stockVolume * lookup_constant("Material :: %s :: Cost" % parent.part.material)

# Estimate the operation times
setupTime = lookup_constant("Machining :: Setup Time")
programTime = (removalVolume / inches**3) * lookup_constant("Machining :: Program Time")
runTime = (removalVolume / inches**3) * lookup_constant("Machining :: Run Time")
inspectTime = (removalVolume / inches**3) * lookup_constant("Machining :: Inspect Time")

# Create the operations
p0 = Process(kind = "Make :: Fabricate :: Stock Machining :: Stock Material",
			 name = "Stock Material",
			 level = "operation",
			 time = 5 * minutes,
			 cost = materialCost,
			 resource = "Machinist")

p1 = Process(kind = "Make :: Fabricate :: Stock Machining :: Setup",
			 name = "Setup",
			 level = "operation",
			 time = setupTime,
			 cost = machinistCost * setupTime,
			 resource = ["Machinist", "3/4/5-axis Mill", "Cutting Tool"],
			 predecessor = p0)
			 
p2 = Process(kind = "Make :: Fabricate :: Stock Machining :: Program",
			 name = "Program",
			 level = "operation",
			 time = programTime,
			 cost = machinistCost * programTime / parent.part.quantity,
			 resource = ["Machinist", "3/4/5-axis Mill", "Cutting Tool"],
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Stock Machining :: Run",
			 name = "Run",
			 level = "operation",
			 time = runTime,
			 cost = machinistCost * runTime,
			 resource = ["Machinist", "3/4/5-axis Mill", "Cutting Tool"],
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Stock Machining :: Inspect",
			 name = "Inspect",
			 level = "operation",
			 time = inspectTime,
			 cost = machinistCost * inspectTime,
			 resource = "Machinist",
			 predecessor = p3)
		
# Finally, link the parent (in this case, the Stock Machining task) to the
# operation chain starting at p0. 
replace(parent, p0)
