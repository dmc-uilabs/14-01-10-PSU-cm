import sys

if not hasattr(parent.part, "suppliers"):
	fail("Part has no suppliers defined for bulk purchasing")

if not hasattr(parent.part, "quantity"):
	fail("Part has no defined quantity")

generalLaborCost = lookup_constant("General Labor :: Labor Rate")

orderTime = 5 * minutes
receiveTime = 10 * minutes
unboxTime = 15 * minutes
	
# pick the option with the smallest excess quantity
options = []

suppliers = parent.part.suppliers
quantity = parent.part.quantity

for supplier in suppliers:
	if supplier["quantity"] > quantity:
		excess = supplier["quantity"] - quantity
		purchaseQuantity = supplier["quantity"]
		purchaseCost = supplier["purchaseCost"]
		leadTime = supplier["leadTime"]

		p1 = Process(kind = "Make :: Bulk Purchase :: Order",
			 name = "Order",
			 level = "operation",
			 time = orderTime,
			 cost = generalLaborCost * orderTime + purchaseCost / purchaseQuantity,
			 excess = excess)
			 
		p2 = Process(kind = "Make :: Bulk Purchase :: Ship",
			 name = "Ship",
			 level = "operation",
			 time = leadTime,
			 cost = 0.0,
			 predecessor = p1)

		options.append((p1, p2))


if len(options) == 0:
	fail("No supplier found for the given quantity: %d" % quantity)
		 
p3 = Process(kind = "Make :: Bulk Purchase :: Receive",
			 name = "Receive",
			 level = "operation",
			 time = receiveTime,
			 cost = generalLaborCost * receiveTime,
			 predecessor = [o[-1] for o in options])
			 
p4 = Process(kind = "Make :: Bulk Purchase :: Unbox",
			 name = "Unbox",
			 level = "operation",
			 time = unboxTime,
			 cost = generalLaborCost * unboxTime,
			 predecessor = p3)
			 
replace(parent, [o[0] for o in options])