if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

stockVolume = parent.part.length * parent.part.width * parent.part.height
partVolume = parent.part.volume
removalVolume = stockVolume - partVolume

machinistCost = lookup_constant("Machinist :: Labor Rate")
materialCost = stockVolume * lookup_constant("Material :: %s :: Cost" % parent.part.material)

setupTime = 5 * minutes
programTime = (removalVolume / inches**3) * 15 * seconds
runTime = (removalVolume / inches**3) * 30 * seconds
inspectTime = (removalVolume / inches**3) * 1 * second

p0 = Process(kind = "Make :: Fabricate :: Stock Machining :: Stock Material",
			 name = "Stock Material",
			 level = "operation",
			 time = 5 * minutes,
			 cost = materialCost)

p1 = Process(kind = "Make :: Fabricate :: Stock Machining :: Setup",
			 name = "Setup",
			 level = "operation",
			 time = setupTime,
			 cost = machinistCost * setupTime,
			 predecessor = p0)
			 
p2 = Process(kind = "Make :: Fabricate :: Stock Machining :: Program",
			 name = "Program",
			 level = "operation",
			 time = programTime,
			 cost = machinistCost * programTime,
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Stock Machining :: Run",
			 name = "Run",
			 level = "operation",
			 time = runTime,
			 cost = machinistCost * runTime,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Stock Machining :: Inspect",
			 name = "Inspect",
			 level = "operation",
			 time = inspectTime,
			 cost = machinistCost * inspectTime,
			 predecessor = p3)
		
replace(parent, p0)
