p1 = Process(kind = "Make :: Purchase",
             name = "Purchase",
             level = "task",
             part = parent.part)

p2 = Process(kind = "Make :: Fabricate",
             name = "Fabricate",
             level = "task",
             part = parent.part)
                    
replace(parent, [p1, p2])