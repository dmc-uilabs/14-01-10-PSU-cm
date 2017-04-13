p1 = Process(kind = "Make :: Fabricate :: Investment Casting",
             name = "Investment Casting",
             level = "task",
             part = parent.part)

p2 = Process(kind = "Make :: Fabricate :: Non-Cored Greensand Casting",
             name = "Non-Cored Greensand Casting",
             level = "task",
             part = parent.part)
                    
replace(parent, [p1, p2])