import unittest
from typing import Any
from memoiz import Memoiz


cache = Memoiz()


class Test:

    @cache
    def identity(self, *args, **kwargs) -> Any:
        return args, kwargs


@cache
def identity(*args, **kwargs) -> Any:
    return args, kwargs


@cache
def callable1(arg0: Any) -> Any:
    return identity(arg0)


class TestAll(unittest.TestCase):

    def test_cache_member(self) -> None:
        cache.clear_all()
        identity({"a": 42})
        self.assertIn(identity, cache._cache)

    def test_cache_callable_member(self) -> None:
        cache.clear_all()
        identity({"a": 42})
        self.assertIn((((("a", 42),),), ()), cache._cache[identity])

    def test_callstack_deadlock(self) -> None:
        cache.clear_all()
        result = callable1(42)
        self.assertEqual(((42,), {}), result)

    def test_cicular_reference(self) -> None:
        cache.clear_all()
        x = []
        x.append(x)
        identity(x)
        self.assertEqual(cache._cache[identity][(((...,),), ())], (([x],), {}))

    def test_cache_entry_removal(self) -> None:
        cache.clear_all()
        identity({"a": 42}, a=42)
        identity({"a": 23}, a=23)
        cache.clear(identity, {"a": 42}, a=42)
        self.assertEqual(cache._cache, {identity: {(((("a", 23),),), ((("a", 23),))): (({"a": 23},), {"a": 23})}})

    def test_cache_callable_removal(self) -> None:
        cache.clear_all()
        identity({"a": 42})
        cache.clear(identity, {"a": 42})
        self.assertEqual(cache._cache, {})

    def test_cache_entry_removal_for_method(self) -> None:
        cache.clear_all()
        test = Test()
        test.identity({"a": 42}, a=42)
        test.identity({"a": 23}, a=23)
        cache.clear(test.identity, {"a": 42}, a=42)
        self.assertEqual(cache._cache, {test.identity: {(((("a", 23),),), (("a", 23),)): (({"a": 23},), {"a": 23})}})

    def test_cache_callable_removal_for_method(self) -> None:
        cache.clear_all()
        test = Test()
        test.identity({"a": 42})
        cache.clear(test.identity, {"a": 42})
        self.assertEqual(cache._cache, {})


if __name__ == "__main__":
    unittest.main()
