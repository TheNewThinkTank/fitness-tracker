import cProfile
import functools


def profile(func):
    """Decorator for profiling a function using cProfile."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)  # Execute the wrapped function

        profiler.disable()
        profiler.dump_stats(f"stats/{func.__name__}.stats")  # Save the stats with the function's name
        return result

    return wrapper
