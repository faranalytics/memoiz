# Memoiz

A thread-safe memoization decorator for functions and methods.

## Introduction

Memoiz provides a function decorator that adds memoization to a function or method. It makes reasonable assumptions about how and if to cache the return value of a function or method based on the arguments passed to it.

## Features

- Use the Memoiz decorator on functions and methods.
- A thread-safe cache.
- Use any number of arguments or keyword arguments.
- Support for parameter and return type hints.
- Handles circular references in dictionaries and lists.
- Support for common unhashable types (e.g., dict, list, set).
- Selective cache entry removal.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Apply Memoization to Class Methods](#apply-memoization-to-class-methods)
  - [Apply Memoization to Functions](#apply-memoization-to-functions)
- [Memoization Strategy](#memoization-strategy)
  - [Type Transformations](#type-transformations)
- [API](#api)
- [Test](#test)

## <h2 id="installation">Installation</h2>

```bash
pip install memoiz
```

## <h2 id="usage">Usage</h2>

### <h3 id="apply-memoization-to-class-methods">Apply Memoization to Class Methods</h3>

In this example you will use Memoiz to memoize the return value of the `greeter.greet` method and print the greeting.

```py
from memoiz import Memoiz

# `cache` is a Python decorator and a callable.
cache = Memoiz()


class Greeter:

    def __init__(self):
        self.adv = "Very"

    @cache # The `cache` decorator adds memoization capabilities to the `greet` method.
    def greet(self, adj: str) -> str:
        return f"Hello, {self.adv} {adj} World!"


greeter = Greeter()

print("1:", cache._cache)

greeting = greeter.greet("Happy")

print("2:", greeting)
```

```bash
1: {}
2: Hello, Very Happy World!
```

As a continuation of the example, you will selectively clear cached articles using the `cache.clear` method.

```python
greeter = Greeter()

print("1:", cache._cache)

greeting = greeter.greet("Happy")

print("2:", greeting)

greeting = greeter.greet("Cautious")

print("3:", greeting)

# The cache has memoized the two method calls.
print("4:", cache._cache)

# Clear the call to `greeter.greet` with the "Happy" argument.
#                          ⮶ args
cache.clear(greeter.greet, "Happy")
#                   ⮴ method

print("5:", cache._cache)

# Clear the call to `greeter.greet` with the `Cautious` argument.
cache.clear(greeter.greet, "Cautious")

# The cache is empty.
print("6:", cache._cache)
```

```bash
1: {}
2: Hello, Very Happy World!
3: Hello, Very Cautious World!
4: {<bound method Greeter.greet of <__main__.Greeter object at 0x7f486842fbe0>>: {(('Happy',), ()): 'Hello, Very Happy World!', (('Cautious',), ()): 'Hello, Very Cautious World!'}}
5: {<bound method Greeter.greet of <__main__.Greeter object at 0x7f486842fbe0>>: {(('Cautious',), ()): 'Hello, Very Cautious World!'}}
6: {}
```

### <h3 id="apply-memoization-to-functions">Apply Memoization to Functions</h3>

In this example you will use Memoiz to memoize the return value of the `greet` function and print the greeting.

```py
from memoiz import Memoiz

cache = Memoiz()


@cache
def greet(adj: str) -> str:
    return f"Hello, {adj} World!"


print("1:", cache._cache)

greeting = greet("Happy")

print("2:", greeting)
```

```bash
1: {}
2: Hello, Happy World!
```

As a continuation of the example, you will selectively clear cached articles using the `cache.clear` method.

```python
print("1:", cache._cache)

greeting = greet("Happy")

print("2:", greeting)

greeting = greet("Cautious")

print("3:", greeting)

print("4:", cache._cache)

#                  ⮶ args
cache.clear(greet, "Happy")
#           ⮴ function

# The cached call using the "Happy" argument is deleted; however, the call using the "Cautious" is still present.
print("5:", cache._cache)

#                  ⮶ args
cache.clear(greet, "Cautious")
#           ⮴ function

# The cache is now empty.
print("6:", cache._cache)
```

```bash
1: {}
2: Hello, Happy World!
3: Hello, Cautious World!
4: {<function greet at 0x7f486842bd00>: {(('Happy',), ()): 'Hello, Happy World!', (('Cautious',), ()): 'Hello, Cautious World!'}}
5: {<function greet at 0x7f486842bd00>: {(('Cautious',), ()): 'Hello, Cautious World!'}}
6: {}
```

## <h2 id="memoization-strategy">Memoization Strategy</h2>

Memoiz will attempt to recursively transform a callable's arguments into a hashable key. The key is used in order to index and look up the callable's return value. The strategy that Memoiz employs for key generation depends on the type of the argument(s) passed to the callable. The [Type Transformations](#type-transformations) table provides examples of how Memoiz transforms arguments of common types.

### <h3 id="type-transformations">Type Transformations</h3>

| Type           | Example      | Hashable Type   | Hashable Representation |
| -------------- | ------------ | --------------- | ----------------------- |
| `dict`         | `{'b':42, 'c': 57, 'a': 23}`   | tuple of tuples | `(('a', 23), ('b', 42), ('c', 57))`          |
| `list`         | `[23, 42, 57]` | tuple           | `(23, 42, 57)`            |
| `tuple`        | `(23, 42, 57)` | tuple           | `(23, 42, 57)`            |
| `set`          | `{23, 42, 57}` | tuple           | `(23, 42, 57)`            |
| hashable types | `hash(...)`  | tuple           | `(Ellipsis,)`           |

> **NB** Dictionaries are sorted by their keys prior to indexing the callable's return value.

## <h2 id="api">API</h2>

### The Memoiz Class

**memoiz.Memoiz(sequentials, mapables, deep_copy)**

- sequentials `Tuple[type, ...]` An optional tuple of types that are assumed to be sequence-like. **Default** `(list, tuple, set)`
- mapables `Tuple[type, ...]` An optional tuple of types that are assumed to be dict-like. **Default** `(dict,)`
- deep_copy `bool` Optionally return the cached return value using Python's `copy.deepcopy`. This can help prevent mutations of the cached return value. **Default:** `True`.

**memoiz.\_\_call\_\_(callable)**

- callable `typing.Callable` The function or method for which you want to add memoization.

A `Memoiz` instance ([see above](#the-cache-class)) is a callable. This is the `@cache` decorator that is used in order to add memoization to a callable. Please see the above [usage](#usage) for how to use this decorator.

**memoiz.clear(callable, \*args, \*\*kwargs)**

- callable `typing.Callable` The callable.
- args `Any` The arguments passed to the callable.
- kwargs `Any` The keyword arguments passed to the callable.

Clears the cache for the specified callable and arguments. See the [usage](#usage) for for how to clear the cache.

**memoiz.clear_all()**

Resets the cache making items in the old cache potentially eligible for garbage collection.

## <h2 id="test">Test</h2>

Clone the repository.

```bash
git clone https://github.com/faranalytics/memoiz.git
```

Change directory into the root of the repository.

```bash
cd memoiz
```

Run the tests.

```bash
python tests/test.py -v
```
