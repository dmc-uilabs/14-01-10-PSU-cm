parts = set()

for predecessor in parent.predecessors:
	if hasattr(predecessor, "part"):
		parts.add(predecessor.part)
		
options = []

if hasattr(parent, "fasteningSteps"):
	for fasteningStep in parent.fasteningSteps:
		p = None

		if fasteningStep["method"] in ["bolt", "bolt (blind)"]:
			p = Process(kind = "Assemble :: Bolting",
						name = "Bolting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)

		if fasteningStep["method"] == "press fit":
			p = Process(kind = "Assemble :: Press Fitting",
						name = "Press Fitting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)

		if fasteningStep["method"] == "snap fit":
			p = Process(kind = "Assemble :: Snap Fitting",
						name = "Snap Fitting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)

		if fasteningStep["method"] == "weld":
			p = Process(kind = "Assemble :: Welding",
						name = "Welding",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)

		if fasteningStep["method"] == "paint":
			p = Process(kind = "Make :: Fabricate :: Paint",
						name = "Painting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)

		if p is None:
			print("Unknown step: %s", fasteningStep["method"])
			#p = Process(kind = "Assemble :: Unknown",
			#			name = "Unknown",
			#			level = "task",
			#			parts = parts,
			#			fasteningStep = fasteningStep)
		
		if p is not None:
			if len(options) > 0:
				p.set_predecessor(options[-1])
			
			options.append(p)
		
if len(options) > 0:
	replace(parent, options[0])
