'''
Library of Process Models
'''

from .exceptions import fail

# These are currently stored internally, but could be changed later to a database
CACHE = {}
CONSTANTS = {}

def register_script(type, script, filename="script"):
    compiled_script = compile(script, filename, mode="exec")
    
    if type in CACHE:
        CACHE[type].append(compiled_script)
    else:
        CACHE[type] = [compiled_script]

def register_file(type, file):
    with open(file) as fp:
        register_script(type, fp.read(), filename=file)
        
def lookup(type):
    return CACHE[type]

def lookup_constant(key, default_value = None):
    try:
        return CONSTANTS[key]
    except KeyError:
        if default_value is None:
            fail("Unable to locate constant " + str(key) + " and no default given")
        else:
            return default_value
    
def set_constant(key, value):
    CONSTANTS[key] = value
