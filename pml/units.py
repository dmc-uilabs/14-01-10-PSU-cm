import logging
from sympy.physics.units import *

LOGGER = logging.getLogger("PML")

dollars = Unit("dollars", "$")
dollars_per_hour = dollars / hours

def as_dollars(value):
    try:
        return "$%.2f" % float(value / dollars)
    except TypeError:
        LOGGER.warning("Unable to convert to dollars: %s", value)
        return "?"
    
def as_time(value):
    try:
        return "%.1f hrs" % float(value / hours)
    except TypeError as e:
        LOGGER.warning("Unable to convert to time: %s", value)
        return "?"