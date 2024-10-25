import inspect
import threading
import copy
from functools import wraps
import logging
from typing import Tuple, Callable, ParamSpec, TypeVar, Any
from .cache_exception import CacheException

P = ParamSpec("P")
T = TypeVar("T")


class Memoiz:

    def __init__(
        self,
        sequentials: Tuple[type, ...] = (list, tuple, set),
        mapables: Tuple[type, ...] = (dict,),
        deep_copy: bool = True,
    ):
        self.deep_copy = deep_copy
        self.sequentials = sequentials
        self.mapables = mapables
        self._cache = {}
        self._lock = threading.Lock()

    def clear(self, callable: Callable, *args, **kwargs) -> None:
        with self._lock:
            args_key = self._freeze((args, kwargs))
            del self._cache[callable][args_key]
            if len(self._cache[callable]) == 0:
                del self._cache[callable]

    def clear_all(self) -> None:
        with self._lock:
            self._cache = {}

    def _freeze(self, it, seen: list = None) -> Any:
        if seen is None:
            seen = []
        try:
            hash(it)
            return it
        except Exception as e:
            pass
        if isinstance(it, self.sequentials):
            if any(it is i for i in seen):
                return ...
            seen.append(it)
            return tuple(self._freeze(i, seen) for i in it)
        elif isinstance(it, self.mapables):
            if any(it is i for i in seen):
                return ...
            seen.append(it)
            return tuple((k, self._freeze(v, seen)) for k, v in sorted(it.items(), key=lambda x: x[0]))

        raise CacheException(f"Cannot freeze {it}.")

    def __call__(self, callable: Callable[P, T]) -> Callable[P, T]:
        @wraps(callable)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                if len(args) != 0 and (
                    hasattr(args[0], callable.__name__)
                    and inspect.unwrap(getattr(args[0], callable.__name__)) is callable
                ):
                    # If the first argument is an object and it contains the method `callable` then use the unwrapped method (i.e., the bound function) for the key.
                    # This is necessary because the bound function is the reference that may be used for clearing a chache entry.
                    callable_key = getattr(args[0], callable.__name__)
                    args_key = self._freeze((args[1:], kwargs))
                else:
                    # If this is not a method call, then use the wrapper for the key.  This is necessary, as referencing the function will return the wrapper.
                    callable_key = wrapper
                    args_key = self._freeze((args, kwargs))

                if callable_key in self._cache and args_key in self._cache[callable_key]:
                    logging.debug(f"Using cache for {(callable_key, args_key)}.")
                    self._lock.acquire()
                    result = self._cache[callable_key][args_key]
                    self._lock.release()
                else:
                    result = callable(*args, **kwargs)
                    with self._lock:
                        if callable_key not in self._cache:
                            self._cache[callable_key] = {}
                        if args_key not in self._cache[callable_key]:
                            self._cache[callable_key][args_key] = result
                            logging.debug(f"Cached {(callable_key, args_key)}.")

                if self.deep_copy:
                    return copy.deepcopy(result)
                else:
                    return result
            except CacheException as e:
                logging.debug(e)
                return callable(*args, **kwargs)
            except BaseException as e:
                if self._lock.locked():
                    self._lock.release()
                raise e

        return wrapper