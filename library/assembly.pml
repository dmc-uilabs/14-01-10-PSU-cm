parts = set()

for predecessor in parent.predecessors:
	if hasattr(predecessor, "part"):
		parts.add(predecessor.part)
		
options = []

if hasattr(parent, "fasteningSteps"):
	for fasteningStep in parent.fasteningSteps:
		if fasteningStep["method"] in ["bolt", "bolt (blind)"]:
			p = Process(kind = "Assemble :: Bolting",
						name = "Bolting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)
		elif fasteningStep["method"] == "press fit":
			p = Process(kind = "Assemble :: Press Fitting",
						name = "Press Fitting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)
		elif fasteningStep["method"] == "snap fit":
			p = Process(kind = "Assemble :: Snap Fitting",
						name = "Snap Fitting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)
		elif fasteningStep["method"] == "weld":
			p = Process(kind = "Assemble :: Welding",
						name = "Welding",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)
		elif fasteningStep["method"] == "paint":
			p = Process(kind = "Make :: Fabricate :: Paint",
						name = "Painting",
						level = "task",
						parts = parts,
						fasteningStep = fasteningStep)
		else:
			p = Process(kind = "Assemble :: Unknown",
						name = "Unknown",
						level = "task")
		
		if len(options) > 0:
			p.set_predecessor(options[-1])
			
		options.append(p)
		
if len(options) > 0:
	replace(parent, options[0])
