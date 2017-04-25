if not hasattr(parent.part, "purchaseCost"):
	fail("Part is not available for purchasing")
	
purchaseCost = parent.part.purchaseCost
leadTime = parent.part.leadTime if hasattr(parent.part, "leadTime") else 7 * days
generalLaborCost = lookup_constant("General Labor :: Labor Rate")

orderTime = lookup_constant("General Labor :: Order Time")
receiveTime = lookup_constant("General Labor :: Receive Time")
unboxTime = lookup_constant("General Labor :: Unbox Time")

p1 = Process(kind = "Make :: Purchase :: Order",
			 name = "Order",
			 level = "operation",
			 time = orderTime,
			 cost = (generalLaborCost * orderTime) / parent.part.quantity + purchaseCost)
			 
p2 = Process(kind = "Make :: Purchase :: Ship",
			 name = "Ship",
			 level = "operation",
			 time = leadTime,
			 cost = 0.0,
			 predecessor = p1)
			 
p3 = Process(kind = "Make :: Purchase :: Receive",
			 name = "Receive",
			 level = "operation",
			 time = receiveTime,
			 cost = generalLaborCost * receiveTime / parent.part.quantity,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Purchase :: Unbox",
			 name = "Unbox",
			 level = "operation",
			 time = unboxTime,
			 cost = generalLaborCost * unboxTime / parent.part.quantity,
			 predecessor = p3)
			 
replace(parent, p1)