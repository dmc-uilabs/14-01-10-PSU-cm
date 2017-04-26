if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

partVolume = parent.part.volume
material = parent.part.material

casterCost = lookup_constant("Casting :: Labor Rate")
materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % material)

meltingTime = (partVolume / inches**3) * lookup_constant("Casting :: Melting Time")
holdingTime = (partVolume / inches**3) * lookup_constant("Casting :: Holding Time")
shakeoutTime = lookup_constant("Casting :: Shakeout Time")
coolingTime = (partVolume / inches**3) * lookup_constant("Casting :: Cooling Time")
finishingTime = lookup_constant("Casting :: Finishing Time")

p1 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting :: Charging and Melting",
			 name = "Charging and Melting",
			 level = "operation",
			 time = meltingTime,
			 cost = casterCost * meltingTime + materialCost,
			 resource = ["Caster"])
			 
p2 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting :: Holding and Pouring",
			 name = "Holding and Pouring",
			 level = "operation",
			 time = holdingTime,
			 cost = casterCost * holdingTime,
			 resource = ["Caster"],
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting :: Shakeout",
			 name = "Shakeout",
			 level = "operation",
			 time = shakeoutTime,
			 cost = casterCost * shakeoutTime,
			 resource = ["Caster"],
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting :: Cooling",
			 name = "Cooling",
			 level = "operation",
			 time = coolingTime,
			 cost = casterCost * coolingTime,
			 resource = ["Caster"],
			 predecessor = p3)
			 
p5 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting :: Finishing",
			 name = "Finishing",
			 level = "operation",
			 time = finishingTime,
			 cost = casterCost * finishingTime,
			 resource = ["Caster"],
			 predecessor = p4)
		
replace(parent, p1)
