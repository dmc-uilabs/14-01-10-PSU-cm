from pml import lookup, register_file

created_processes = []

class Process(object):
    
    def __init__(self, kind, **kwargs):
        self.kind = kind
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        created_processes.append(self)
        
    def __repr__(self):
        return self.name

def expand(process, script):
    global created_processes
    created_processes = []
    env = dict(globals(), parent=process, graph=5)
    eval(script, env, {})
    print(created_processes)
    
register_file("script", "library/script.pml")
expand(25, lookup("script")[0])
expand(30, lookup("script")[0])
expand(35, lookup("script")[0])