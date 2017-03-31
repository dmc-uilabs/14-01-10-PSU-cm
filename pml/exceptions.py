class FailedRouting(Exception):
    pass

def fail(message):
    raise FailedRouting(message)