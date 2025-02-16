import functools
import time


def retry_on_none(retries=5, delay=1):
    """Decorator to retry a function up to a specified number of times if it returns None.

    Args:
        retries (int): The maximum number of retries. Defaults to 5.
        delay (int): The delay between retries in seconds. Defaults to 1 second.
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            for attempt in range(retries):
                result = func(*args, **kwargs)
                if result is not None:
                    print(f"Function succeeded on attempt {attempt + 1}")
                    return result
                else:
                    print(f"Attempt {attempt + 1} failed; retrying...")
                    time.sleep(delay)
            print("All retries failed.")
            return None
        return wrapper_retry
    return decorator_retry
