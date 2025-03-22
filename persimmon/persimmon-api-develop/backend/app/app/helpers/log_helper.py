import time
from functools import wraps

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Logs the execution time of the decorated function.

        :param func: The function to be decorated
        :type func: function
        :return: The result of the decorated function
        :rtype: object
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        print(f"{func.__name__} took {duration:.4f}s")  
        return result
    return wrapper