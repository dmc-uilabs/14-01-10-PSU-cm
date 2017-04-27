'''
Library of Process Models
'''

import os
import json
import logging
from .exceptions import fail
from .units import *

LOGGER = logging.getLogger("PML")

# Case insensitive dictionary for string keys courtesy of http://stackoverflow.com/a/32888599
class CaseInsensitiveDict(dict):
    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key
    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()
    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__class__._k(key))
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(self.__class__._k(key), value)
    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(self.__class__._k(key))
    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(self.__class__._k(key))
    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(self.__class__._k(key))
    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(self.__class__._k(key), *args, **kwargs)
    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(self.__class__._k(key), *args, **kwargs)
    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(self.__class__._k(key), *args, **kwargs)
    def update(self, E={}, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))
    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)

# These are currently stored internally, but could be changed later to a database
CACHE = CaseInsensitiveDict()
CONSTANTS = CaseInsensitiveDict()

def register_script(type, script, filename="script"):
    compiled_script = compile(script, filename, mode="exec")
    
    if type in CACHE:
        CACHE[type].append(compiled_script)
    else:
        CACHE[type] = [compiled_script]

def register_file(type, file):
    LOGGER.info("Registering %s as %s", file, type)
    with open(file) as fp:
        register_script(type, fp.read(), filename=file)
    
# WARNING: This method modifies the current working directory so that filenames
# can be given relative to the containing folder.  It will restore the original
# directory when finished.
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
    
def load_constants(file):
    with open(file, "r") as f:
        content = json.load(f)
        
    for item in content:
        name = item["name"]
        value = item["value"]
        
        if "unit" in item:
            unit = eval(item["unit"], {}, globals())
            value *= unit
            
        set_constant(name, value)

def print_constants():
    for key in CONSTANTS.keys():
        print(key, CONSTANTS[key])