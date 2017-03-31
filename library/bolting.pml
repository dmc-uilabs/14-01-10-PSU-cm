quantity = parent.fasteningStep["quantity"] if "quantity" in parent.fasteningStep else 1
generalLaborCost = lookup_constant("General Labor :: Labor Rate")
boltTime = quantity * 30 * seconds

p = Process(kind = "Assemble :: Bolting :: Bolt",
			name = "Bolt" if quantity == 1 else ("Bolt x %d" % quantity),
			level = "operation",
			time = boltTime,
			cost = boltTime * generalLaborCost)
			
replace(parent, p)