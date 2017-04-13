'''
Library of Process Models
'''

import os
from .exceptions import fail
from .units import *

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
    print("Registering", file, "as", type)
    with open(file) as fp:
        register_script(type, fp.read(), filename=file)
    
# WARNING: This method modifies the current working directory so that filenames
# can be given relative to the containing folder.    
def auto_register(folder):
    init_dir = os.getcwd()
    os.chdir(folder)
    
    init_filename = "__init__.pml"
    
    if os.path.exists(init_filename) and os.path.isfile(init_filename):
        with open(init_filename) as fp:
            init_script = compile(fp.read(), init_filename, mode="exec")
            eval(init_script, {}, globals())
        
    for file in os.listdir():
        if os.path.isdir(file):
            auto_register(file)
            
    os.chdir(init_dir)
        
def lookup(type):
    return CACHE[type]

def has_constant(key):
    return key in CONSTANTS

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
