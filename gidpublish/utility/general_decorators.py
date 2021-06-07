
# region [Imports]

from functools import wraps
import os
from time import time

# endregion[Imports]


def debug_timing_print(func):
    @wraps(func)
    def _function_print_time(*args, **kwargs):
        start_time = time()
        _out = func(*args, **kwargs)

        if len(args) != 0 and hasattr(args[0], func.__name__):
            report = f"'{func.__name__}' of the '{args[0].__class__.__name__}' class took {str(round(time()-start_time, ndigits=4))} seconds"
        else:
            report = f"'{func.__name__}' took {str(round(time()-start_time, ndigits=4))} seconds"

        print(report)
        return _out
    if os.getenv('IS_DEV') == 'true':
        return _function_print_time
    else:
        return func


def debug_timing_log(logger):
    def _decorator(func):
        @wraps(func)
        def _function_print_time(*args, **kwargs):
            start_time = time()
            _out = func(*args, **kwargs)
            if len(args) != 0 and hasattr(args[0], func.__name__):
                report = f"'{func.__name__}' of '{str(args[0])}' took {str(round(time()-start_time, ndigits=4))} seconds"
            else:
                report = f"'{func.__name__}' took {str(round(time()-start_time, ndigits=4))} seconds"

            logger.debug(report, extra={'func_name_override': func.__name__})
            return _out
        if os.getenv('IS_DEV') == 'true':
            return _function_print_time
        else:
            return func
    return _decorator
