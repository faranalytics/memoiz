import unittest
from typing import Any
from collections import OrderedDict
from memoiz import Memoiz


class TestCase(unittest.TestCase):

    def setUp(self) -> None:

        cache = Memoiz()

        class Test:

            @cache
            def identity(self, *args, **kwargs) -> Any:
                return args, kwargs

        @cache
        def identity(*args, **kwargs) -> Any:
            return args, kwargs

        @cache
        def callable(arg0: Any) -> Any:
            return identity(arg0)

        self.cache = cache
        self.test = Test()
        self.identity = identity
        self.callable = callable

    def test_cache_member(self) -> None:
        self.identity({"a": 42})
        self.assertIn(self.identity, self.cache._cache)

    def test_cache_callable_member(self) -> None:
        self.identity({"a": 42})
        self.assertIn((((("a", 42),),), ()), self.cache._cache[self.identity])

    def test_callstack_deadlock(self) -> None:
        result = self.callable(42)
        self.assertEqual(((42,), {}), result)

    def test_cicular_reference(self) -> None:
        x = []
        x.append(x)
        self.identity(x)
        self.assertEqual(self.cache._cache[self.identity][(((...,),), ())], (([x],), {}))

    def test_cache_entry_removal(self) -> None:
        self.identity({"a": 42}, a=42)
        self.identity({"a": 23}, a=23)
        self.cache.clear(self.identity, {"a": 42}, a=42)
        self.assertEqual(
            self.cache._cache, {self.identity: {(((("a", 23),),), ((("a", 23),))): (({"a": 23},), {"a": 23})}}
        )

    def test_cache_callable_removal(self) -> None:
        self.identity({"a": 42})
        self.cache.clear(self.identity, {"a": 42})
        self.assertEqual(self.cache._cache, {})

    def test_cache_entry_removal_for_method(self) -> None:
        self.test.identity({"a": 42}, a=42)
        self.test.identity({"a": 23}, a=23)
        self.cache.clear(self.test.identity, {"a": 42}, a=42)
        self.assertEqual(
            self.cache._cache, {self.test.identity: {(((("a", 23),),), (("a", 23),)): (({"a": 23},), {"a": 23})}}
        )

    def test_cache_callable_removal_for_method(self) -> None:
        self.test.identity({"a": 42})
        self.cache.clear(self.test.identity, {"a": 42})
        self.assertEqual(self.cache._cache, {})

    def test_deterministic_representation_of_sets(self) -> None:
        for _ in range(0, int(1e4)):
            s1 = {23, "42", 57, ...}
            s2 = {..., 23, "42", 57}
            self.assertEqual(s1, s2)
            self.identity(s1)
            self.identity(s2)
            self.assertEqual(len(self.cache._cache[self.identity]), 1)

    def test_deterministic_representation_of_dicts(self) -> None:
        for _ in range(0, int(1e4)):
            d1 = {...: 57, "a": 23, "b": 42}
            d2 = {"b": 42, "a": 23, ...: 57}
            self.assertEqual(d1, d2)
            self.identity(d1)
            self.identity(d2)
            self.assertEqual(len(self.cache._cache[self.identity]), 1)

    def test_insertion_order_of_ordereddicts(self) -> None:
        d1 = OrderedDict(a=23, b=42, c=57)
        d2 = OrderedDict(c=57, b=42, a=23)
        d3 = OrderedDict(c=57, b=42, a=23)
        self.assertNotEqual(d1, d2)
        self.identity(d1)
        self.identity(d2)
        self.identity(d3)
        self.assertEqual(len(self.cache._cache[self.identity]), 2)


if __name__ == "__main__":
    unittest.main()
