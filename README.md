# Memoiz

A decorator for adding memoization to functions and methods.

## Introduction

Memoiz provides a function decorator that adds memoization to a function or method. It makes reasonable assumptions about how and if to cache the return value of a function or method based on the arguments passed to the callable.

## Features

- Use the Memoiz decorator on functions and methods.
- A thread-safe cache.
- Call your function or method with any number of arguments or keyword arguments.
- Support for parameter and return type hints.
- Handles circular references in dictionaries, lists, sets, and tuples.
- Support for common unhashable types (e.g., dict, list, set).
- Selective cache entry removal.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Apply Memoization to Class Methods](#apply-memoization-to-class-methods)
  - [Apply Memoization to Functions](#apply-memoization-to-functions)
- [Memoization Strategy](#memoization-strategy)
  - [Type Transformations of Common Types](#type-transformations-of-common-types)
- [API](#api)
- [Versioning](#versioning)
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

# `cache` is a Python decorator.
cache = Memoiz()


class Greeter:

    def __init__(self):
        self.adv = "Very"

    # The `cache` decorator adds memoization capabilities to the `greet` method.
    @cache
    def greet(self, adj: str) -> str:
        return f"Hello, {self.adv} {adj} World!"


greeter = Greeter()

# The cache is empty.
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

# The cache is empty.
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

# The cache is empty.
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
# The cache is empty.
print("1:", cache._cache)

greeting = greet("Happy")

print("2:", greeting)

greeting = greet("Cautious")

print("3:", greeting)

# Both the `Happy` and `Cautious` call have been cached.
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

Memoiz will attempt to recursively transform a callable's arguments into a hashable key. The key is used in order to index and look up the callable's return value. The strategy that Memoiz employs for key generation depends on the type of the argument(s) passed to the callable. The [Type Transformations of Common Types](#type-transformations-of-common-types) table provides examples of how Memoiz transforms arguments of common types.

### <h3 id="type-transformations-of-common-types">Type Transformations of Common Types</h3>

| Type           | Example                      | Hashable Representation             |
| -------------- | ---------------------------- | ----------------------------------- |
| `dict`         | `{'b':42, 'c': 57, 'a': 23}` | `(('a', 23), ('b', 42), ('c', 57))` |
| `list`         | `[23, 42, 57]`               | `(23, 42, 57)`                      |
| `tuple`        | `(23, 42, 57)`               | `(23, 42, 57)`                      |
| `set`          | `{..., 23, "42", 57}`        | `(23, '42', 57, Ellipsis)`          |
| hashable types | `...`                        | `(Ellipsis,)`                       |

#### Dictionaries

By default a dictionary is sorted by the string representation of its keys prior to indexing the callable's return value. If you wish to rely on the iteration order of `dict` instances you can specify this preference as an argument to the `sortables` parameter of the [Memoiz](#the-memoiz-class) constructor (e.g., pass in the tuple `(set,)` in order to override the default).

#### Sets

By default a set is sorted by the string representation of its values prior to indexing the callable's return value.

## <h2 id="api">API</h2>

### <h3 id="the-memoiz-class">The Memoiz Class</h3>

**memoiz.Memoiz(iterables, mappables, sortables, deep_copy)**

- iterables `Tuple[type, ...]` An optional tuple of types that are assumed to be iterables. **Default** `(list, tuple, set)`
- mappables `Tuple[type, ...]` An optional tuple of types that are assumed to be mappings. **Default** `(dict, OrderedDict)`
- sortables `Tuple[type, ...]` An optional tuple of types that are sorted by the string representation of their keys or values prior to indexing the return value. **Default** `(dict, set)`
- deep_copy `bool` Optionally return the cached return value using Python's `copy.deepcopy`. This can help prevent mutations of the cached return value. **Default:** `True`.

**memoiz.\_\_call\_\_(callable)**

- callable `typing.Callable` The function or method for which you want to add memoization.

A `Memoiz` instance is a callable. This is the `@cache` decorator (see [Usage](#usage) above) that is used in order to add memoization to a callable.

**memoiz.clear(callable, \*args, \*\*kwargs)**

- callable `typing.Callable` The callable.
- args `Any` The arguments passed to the callable.
- kwargs `Any` The keyword arguments passed to the callable.

Clears the cache for the specified callable and arguments. See [Usage](#usage) for for how to clear the cache.

**memoiz.clear_all()**

Resets the cache making released items potentially eligible for garbage collection.

**memoiz.clear_callable(callable)**

Clears the cache and all the entries for the specified callable.

## <h2 id="versioning">Versioning</h2>

The Memoiz package strictly adheres to semantic versioning. Breaking changes to the public API will result in a turn of the major. Minor and patch changes will always be backward compatible.

Excerpted from [Semantic Versioning 2.0.0](https://semver.org/):

> Given a version number MAJOR.MINOR.PATCH, increment the:
>
> 1. MAJOR version when you make incompatible API changes
> 2. MINOR version when you add functionality in a backward compatible manner
> 3. PATCH version when you make backward compatible bug fixes
>
> Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

## <h2 id="test">Test</h2>

Clone the repository.

```bash
git clone https://github.com/faranalytics/memoiz.git
```

Change directory into the root of the repository.

```bash
cd memoiz
```

Install the package in editable mode.

```bash
pip install -e .
```

Run the tests.

```bash
python -m unittest -v
```
