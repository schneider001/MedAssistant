from functools import wraps
import time
from DB.log_init import *

def retry(exceptions=Exception, total_tries=3, delay=0.5, logger=logger):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries = total_tries
            print_args = args if args else 'no args'
            while _tries > 0:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    if _tries == 0:
                        msg = str(f'Function: {f.__name__}\n'
                                  f'Failed despite best efforts after {total_tries} tries.\n'
                                  f'args: {print_args}, kwargs: {kwargs}')
                        logger.exception(msg)
                        raise
                    msg = str(f'Function: {f.__name__}\n'
                              f'Exception: {e}\n'
                              f'Retrying in {delay} seconds!, args: {print_args}, kwargs: {kwargs}\n')
                    logger.warning(msg)
                    time.sleep(delay)
        return func_with_retries
    return retry_decorator

