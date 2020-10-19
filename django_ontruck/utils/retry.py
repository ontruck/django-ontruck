from functools import wraps, partial
from time import sleep


def decorator(caller):
    def decor(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return caller(f, *args, **kwargs)
        return wrapper
    return decor


def retry(tries, delay, backoff=1):
    @decorator
    def retry_decorator(f, *fargs, **fkwargs):
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return __retry(partial(f, *args, **kwargs), tries, delay, backoff)

    return retry_decorator


def __retry(f, tries, delay, backoff=1):
    _tries, _delay = tries, delay

    while _tries:
        try:
            return f()
        except Exception:
            _tries -= 1
            sleep(delay)
            _delay *= backoff
