if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

sorted_dimensions = sorted([parent.part.length, parent.part.width, parent.part.height])
thickness = sorted_dimensions[0]
cutLength = sorted_dimensions[1] * sorted_dimensions[2]
partVolume = parent.part.length * parent.part.width * parent.part.height

if thickness > 1 * inch:
	fail("Part is too thick for plate/sheet")
	
machinistCost = lookup_constant("Machinist :: Labor Rate")
materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % parent.part.material)
setupTime = 5 * minutes
programTime = (cutLength / inches**2) * 15 * seconds
runTime = (cutLength / inches**2) * 30 * seconds
inspectTime = (cutLength / inches**2) * 1 * second

p0 = Process(kind = "Make :: Fabricate :: Stock Machining :: Stock Material",
			 name = "Stock Material",
			 level = "operation",
			 time = 5 * minutes,
			 cost = materialCost,
			 requires = ["Welder"])

p1 = Process(kind = "Make :: Fabricate :: Plate/Sheet :: Setup",
			 name = "Setup",
			 level = "operation",
			 time = setupTime,
			 cost = machinistCost * setupTime,
			 predecessor = p0)
			 
p2 = Process(kind = "Make :: Fabricate :: Plate/Sheet :: Program",
			 name = "Program",
			 level = "operation",
			 time = programTime,
			 cost = machinistCost * programTime,
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Plate/Sheet :: Run",
			 name = "Run",
			 level = "operation",
			 time = runTime,
			 cost = machinistCost * runTime,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Plate/Sheet :: Inspect",
			 name = "Inspect",
			 level = "operation",
			 time = inspectTime,
			 cost = machinistCost * inspectTime,
			 predecessor = p3)
		
replace(parent, p0)
