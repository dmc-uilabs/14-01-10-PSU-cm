import sys

if not hasattr(parent.part, "suppliers"):
	fail("Part has no suppliers defined for bulk purchasing")

if not hasattr(parent.part, "quantity"):
	fail("Part has no defined quantity")
	
# pick the option with the smallest excess quantity
suppliers = parent.part.suppliers
quantity = parent.part.quantity
excess = sys.maxsize

for supplier in suppliers:
	if supplier["quantity"] > quantity and supplier["quantity"] - quantity < excess:
		excess = supplier["quantity"] - quantity
		purchaseQuantity = supplier["quantity"]
		purchaseCost = supplier["purchaseCost"]
		leadTime = supplier["leadTime"]

if excess == sys.maxsize:
	fail("No supplier found for the given quantity: %d" % quantity)

generalLaborCost = lookup_constant("General Labor :: Labor Rate")

orderTime = 5 * minutes
receiveTime = 10 * minutes
unboxTime = 15 * minutes

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
			 
p3 = Process(kind = "Make :: Bulk Purchase :: Receive",
			 name = "Receive",
			 level = "operation",
			 time = receiveTime,
			 cost = generalLaborCost * receiveTime,
			 predecessor = p2)
			 
p4 = Process(kind = "Make :: Bulk Purchase :: Unbox",
			 name = "Unbox",
			 level = "operation",
			 time = unboxTime,
			 cost = generalLaborCost * unboxTime,
			 predecessor = p3)
			 
replace(parent, p1)