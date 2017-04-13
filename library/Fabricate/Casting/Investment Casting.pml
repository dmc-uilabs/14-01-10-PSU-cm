if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

partVolume = parent.part.volume
material = parent.part.material

casterCost = lookup_constant("Caster :: Labor Rate")
materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % material)

meltingTime = (partVolume / inches**3) * 2 * minutes
moldingTime = (partVolume / inches**3) * 90 * seconds
shakeoutTime = 1 * minute
coolingTime = (partVolume / inches**3) * 10 * seconds
finishingTime = 5 * minutes

p1 = Process(kind = "Make :: Fabricate :: Investment Casting :: Melting",
			 name = "Melting",
			 level = "operation",
			 time = meltingTime,
			 cost = casterCost * meltingTime + materialCost,
			 resource = ["Caster"])
			 
p2 = Process(kind = "Make :: Fabricate :: Investment Casting :: Molding and Pouring",
			 name = "Molding and Pouring",
			 level = "operation",
			 time = moldingTime,
			 cost = casterCost * moldingTime,
			 resource = ["Caster"],
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Investment Casting :: Shakeout",
			 name = "Shakeout",
			 level = "operation",
			 time = shakeoutTime,
			 cost = casterCost * shakeoutTime,
			 resource = ["Caster"],
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Investment Casting :: Cooling",
			 name = "Cooling",
			 level = "operation",
			 time = coolingTime,
			 cost = casterCost * coolingTime,
			 resource = ["Caster"],
			 predecessor = p3)
			 
p5 = Process(kind = "Make :: Fabricate :: Investment Casting :: Finishing",
			 name = "Finishing",
			 level = "operation",
			 time = finishingTime,
			 cost = casterCost * finishingTime,
			 resource = ["Caster"],
			 predecessor = p4)
		
replace(parent, p1)
