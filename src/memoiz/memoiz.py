import inspect
import threading
import copy
from functools import wraps
import logging
from typing import Tuple, Callable, ParamSpec, TypeVar, Any
from collections import OrderedDict
from .cache_exception import CacheException

P = ParamSpec("P")
T = TypeVar("T")


class Memoiz:

    def __init__(
        self,
        iterables: Tuple[type, ...] = (list, tuple, set),
        mappables: Tuple[type, ...] = (dict, OrderedDict),
        sortables: Tuple[type, ...] = (dict, set),
        deep_copy: bool = True,
        *args,
        **kwargs,
    ):
        self.deep_copy = deep_copy
        self.mappables = mappables
        self.iterables = iterables
        self.sortables = sortables
        self._cache = {}
        self._lock = threading.Lock()

    def clear(self, callable: Callable, *args, **kwargs) -> None:
        with self._lock:
            args_key = self._freeze((args, kwargs))
            del self._cache[callable][args_key]
            if len(self._cache[callable]) == 0:
                del self._cache[callable]

    def clear_callable(self, callable: Callable) -> None:
        with self._lock:
            del self._cache[callable]

    def clear_all(self) -> None:
        self._cache = {}

    def _freeze(self, it: Any, seen: list = None) -> Any:
        if seen is None:
            seen = []
        try:
            hash(it)
            return it
        except Exception as e:
            pass
        if isinstance(it, self.iterables):
            if any(it is i for i in seen):
                return str(it)
            seen.append(it)
            if type(it) in self.sortables:
                it = sorted(it, key=str)
            return tuple(self._freeze(i, seen) for i in it)
        elif isinstance(it, self.mappables):
            if any(it is i for i in seen):
                return str(it)
            seen.append(it)
            if type(it) in self.sortables:
                its = sorted(it.items(), key=lambda x: str(x[0]))
            else:
                its = it.items()
            return tuple((k, self._freeze(v, seen)) for k, v in its)

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
