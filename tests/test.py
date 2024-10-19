import unittest
from typing import Any
from memoiz import Memoiz

cache = Memoiz()


@cache
def identity(arg0: Any) -> Any:

    return arg0


@cache
def callable1(arg0: Any) -> Any:

    return callable2(arg0)


@cache
def callable2(arg0: Any) -> Any:

    return arg0

class Test(unittest.TestCase):

    def test_cache_member(self) -> None:

        identity({"a": 42})

        self.assertIn(identity, cache._cache)

    def test_cache_callable_member(self) -> None:

        identity({"a": 42})

        self.assertIn((((("a", 42),),), ()), cache._cache[identity])

    def test_callstack_deadlock(self) -> None:

        result = callable1(42)

        self.assertEqual(42, result)


if __name__ == "__main__":
    unittest.main()
