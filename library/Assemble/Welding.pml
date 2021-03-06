parts = parent.parts
materials = set([part.material for part in parts])
weldLength = parent.fasteningStep["weldLength"]
twoSided = parent.fasteningStep["twoSided"] if "twoSided" in parent.fasteningStep else False
requiresXRay = parent.fasteningStep["requiresXRay"] if "requiresXRay" in parent.fasteningStep else False

if len(materials) > 1:
	fail("Unable to weld parts with different materials")
	
for part in parts:
	if hasattr(part, "coating") and part.coating == "Paint":
		fail("Unable to weld painted parts, painting needs to occur after assembly")

if twoSided:
	weldLength *= 2
	
welderCost = lookup_constant("Welding :: Labor Rate")
xrayCost = lookup_constant("X-Ray Machine :: Cost")
weldMaterialCost = lookup_constant("Material :: Weld Filler :: Cost")

prepareTime = (weldLength / inches) * lookup_constant("Welding :: Prepare Time")
weldTime = (weldLength / inches) * lookup_constant("Welding :: Weld Time")
visualInspectionTime = (weldLength / inches) * lookup_constant("Welding :: Visual Inspection Time")
xrayInspectionTime = lookup_constant("X-Ray Machine :: Setup Time") + ((weldLength / inches) * lookup_constant("X-Ray Machine :: Scan Time"))
	
p1 = Process(kind = "Assemble :: Welding :: Prepare Joint",
			 name = "Prepare Joint",
			 level = "operation",
			 time = prepareTime,
			 cost = prepareTime * welderCost,
			 resource = "Welder")
			 
p2 = Process(kind = "Assemble :: Welding :: Weld Joint",
			 name = "Weld Joint",
			 level = "operation",
			 predecessor = p1,
			 time = weldTime,
			 cost = weldTime * welderCost,
			 resource = "Welder")
	
if not requiresXRay:		 
	p3 = Process(kind = "Assemble :: Welding :: Visual Inspection",
				 name = "Visual Inspection",
				 level = "operation",
				 predecessor = p2,
				 time = visualInspectionTime,
				 cost = visualInspectionTime * welderCost,
				 resource = "Welder")
else:	
	p3 = Process(kind = "Assemble :: Welding :: X-Ray Inspection",
			 	 name = "X-Ray Inspection",
			 	 level = "operation",
			 	 predecessor = p2,
			 	 time = xrayInspectionTime,
			 	 cost = xrayInspectionTime * welderCost + xrayCost,
			 	 resource = ["Welder", "X-Ray Machine"])
			 
replace(parent, p1)