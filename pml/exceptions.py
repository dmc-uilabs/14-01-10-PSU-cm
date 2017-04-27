class FailedRouting(Exception):
    pass

class NoPathException(Exception):
    pass

class MultiplePathException(Exception):
    pass

def fail(message):
    raise FailedRouting(message)