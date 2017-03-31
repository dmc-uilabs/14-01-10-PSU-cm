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
	if parent.part.coating == "Paint":
		p4 = Process(kind = "Make :: Fabricate :: Paint",
					 name = "Paint",
					 level = "task",
					 part = parent.part,
					 predecessor = [p1, p2, p3])
			 
replace(parent, [p1, p2, p3]) 