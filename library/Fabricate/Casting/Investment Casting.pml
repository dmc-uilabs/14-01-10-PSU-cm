import math

if not hasattr(parent.part, "material"):
	fail("Part has no defined material")

if not hasattr(parent.part, "quantity"):
	fail("Part has no defined quantity")

partVolume = parent.part.volume
material = parent.part.material

casterCost = lookup_constant("Casting :: Labor Rate")
materialCost = partVolume * lookup_constant("Material :: %s :: Cost" % material)

# estimate the number of batches
totalVolume = parent.part.length * parent.part.width * parent.part.height
batchQuantity = math.floor(lookup_constant("Investment Casting :: Batch Volume") / totalVolume)
batches = math.ceil(parent.part.quantity / min(batchQuantity, parent.part.quantity))

# estimate the time based on part volume
meltingTime = (partVolume / inches**3) * lookup_constant("Casting :: Melting Time")
moldingTime = (partVolume / inches**3) * lookup_constant("Casting :: Molding Time")
shakeoutTime = lookup_constant("Casting :: Shakeout Time")
coolingTime = (partVolume / inches**3) * lookup_constant("Casting :: Cooling Time")
finishingTime = lookup_constant("Casting :: Finishing Time")

# create the casting operations
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
			 cost = casterCost * moldingTime / batches,
			 resource = ["Caster"],
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Fabricate :: Investment Casting :: Shakeout",
			 name = "Shakeout",
			 level = "operation",
			 time = shakeoutTime,
			 cost = casterCost * shakeoutTime / batches,
			 resource = ["Caster"],
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Fabricate :: Investment Casting :: Cooling",
			 name = "Cooling",
			 level = "operation",
			 time = coolingTime,
			 cost = casterCost * coolingTime / batches,
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
