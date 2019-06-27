"""Simple decorator to measure a function and output the length of time the function took in seconds."""
import time
import logging
from functools import wraps


def latency_logger(name):
    """Measuring performance of function and log latency."""
    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)

        @wraps(func)
        def wrapper(*args, **kwargs):
            s = time.time()
            rtn = func(*args, **kwargs)
            e = time.time()
            log.info("{}  function {}() took {} s".format(logname, func.__name__, e - s))
            return rtn
        return wrapper
    return decorate
