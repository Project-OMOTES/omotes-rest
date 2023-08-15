import time

from functools import wraps
from tno.shared.log import get_logger

logger = get_logger(__name__)



def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        runtime = round(end - start, 2)
        logger.debug(
            "{} ran in {}s".format(func.__name__, runtime),
            function=func.__name__,
            runtime=runtime,
        )
        return result

    return wrapper
