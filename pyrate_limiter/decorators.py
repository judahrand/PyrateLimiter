from functools import wraps
from time import sleep
from pyrate_limiter.exceptions import BucketFullException


class RateLimitDecorator(object):
    """
    Rate limit decorator class.
    """
    def __init__(self, bucket_limiter, raise_on_limit=True):
        """
        Instantiate a RateLimitDecorator based on a BucketLimiter class.
        :param bucker_limiter calls: An instance of a BucketLimiter class.
        :param bool raise_on_limit: A boolean allowing the caller to avoiding rasing an exception.
        """
        self.bucket_limiter = bucket_limiter
        self.raise_on_limit = raise_on_limit

    def __call__(self, func):
        """
        Return a wrapped function that prevents further function invocations if
        previously the ratelimit has been exceeded.
        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        """
        @wraps(func)
        def wrapper(*args, **kargs):
            """
            Extend the behaviour of the decorated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.
            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: BucketFullException
            """
            try:
                self.bucket_limiter.append(None)
            except BucketFullException as e:
                if self.raise_on_limit:
                    raise e
                return

            return func(*args, **kargs)
        return wrapper

def sleep_and_retry(func):
    """
    Return a wrapped function that rescues bucket full exceptions, sleeping the
    current thread until bucket resets.
    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    """
    @wraps(func)
    def wrapper(*args, **kargs):
        """
        Call the rate limited function. If the function raises a bucket full
        exception sleep for half a second and retry the function.
        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyworded variable length argument list to the decorated function.
        """
        while True:
            try:
                return func(*args, **kargs)
            except BucketFullException:
                sleep(0.5)
    return wrapper
