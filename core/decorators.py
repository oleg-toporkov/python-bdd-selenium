"""
Created on September 18, 2015

@author: oleg-toporkov
"""
from functools import wraps
import logging


def log_exception(message, logger=None):
    """
    Decorator for function execution in try/except with first logging what tried to do and then raising an exception
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if logger is None:
                _self = args[0]  # self
                log = getattr(_self, 'logger')
            else:
                log = logger
            assert isinstance(log, logging.Logger)
            try:
                return func(*args, **kwargs)
            except Exception:
                log.error(message.format(args[1]))
                raise
        return wrapper
    return decorator
