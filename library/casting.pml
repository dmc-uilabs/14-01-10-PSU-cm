if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

partVolume = parent.part.volume

casterCost = lookup_constant("Caster :: Labor Rate")
materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % parent.part.material)

meltingTime = (partVolume / inches**3) * 2 * minutes
moldingTime = (partVolume / inches**3) * 90 * seconds
shakeoutTime = 1 * minute
cleaningTime = (partVolume / inches**3) * 10 * seconds
finishingTime = 5 * minutes

p1 = Process(kind = "Make :: Fabricate :: Casting :: Melting",
			 name = "Melting",
			 level = "operation",
			 time = meltingTime,
			 cost = casterCost * meltingTime + materialCost)
			 
p2 = Process(kind = "Make :: Fabricate :: Casting :: Molding and Coring",
			 name = "Molding and Coring",
			 level = "operation",
			 time = moldingTime,
			 cost = casterCost * moldingTime,
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Casting :: Shakeout",
			 name = "Shakeout",
			 level = "operation",
			 time = shakeoutTime,
			 cost = casterCost * shakeoutTime,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Casting :: Cleaning",
			 name = "Cleaning",
			 level = "operation",
			 time = cleaningTime,
			 cost = casterCost * cleaningTime,
			 predecessor = p3)
			 
p5 = Process(kind = "Make :: Fabricate :: Casting :: Finishing",
			 name = "Finishing",
			 level = "operation",
			 time = finishingTime,
			 cost = casterCost * finishingTime,
			 predecessor = p4)
		
replace(parent, p1)
