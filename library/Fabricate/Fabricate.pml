p1 = Process(kind = "Make :: Fabricate :: Stock Machining",
			 name = "Stock Machining",
			 level = "task",
			 part = parent.part)
			 
p2 = Process(kind = "Make :: Fabricate :: Casting",
			 name = "Casting",
			 level = "task",
			 part = parent.part)
			 
p3 = Process(kind = "Make :: Fabricate :: Plate/Sheet",
			 name = "Plate/Sheet",
			 level = "task",
			 part = parent.part)
			 
if hasattr(parent.part, "coating"):
	if parent.part.coating == "Chromium Plating":
		p4 = Process(kind = "Make :: Fabricate :: Chromium Plating",
					 name = "Chromium Plating",
					 level = "task",
					 part = parent.part,
					 predecessor = [p1, p2, p3])
	elif parent.part.coating == "Paint" or parent.part.coating == "Liquid Top Coating":
		p4 = Process(kind = "Make :: Fabricate :: Liquid Priming",
					 name = "Liquid Priming",
					 level = "task",
					 part = parent.part,
					 predecessor = [p1, p2, p3])
		p5 = Process(kind = "Make :: Fabricate :: Liquid Top Coating",
					 name = "Liquid Top Coating",
					 level = "task",
					 part = parent.part,
					 predecessor = p4)
	elif parent.part.coating == "Powder" or parent.part.coating == "Powder Top Coating":
		p4 = Process(kind = "Make :: Fabricate :: Powder Priming",
					 name = "Powder Priming",
					 level = "task",
					 part = parent.part,
					 predecessor = [p1, p2, p3])
		p5 = Process(kind = "Make :: Fabricate :: Powder Top Coating",
					 name = "Powder Top Coating",
					 level = "task",
					 part = parent.part,
					 predecessor = p4)
	elif parent.part.coating == "Phosphate Coating":
		p4 = Process(kind = "Make :: Fabricate :: Phosphate Coating",
					 name = "Phosphate Coating",
					 level = "task",
					 part = parent.part,
					 predecessor = [p1, p2, p3])
			 
replace(parent, [p1, p2, p3]) 