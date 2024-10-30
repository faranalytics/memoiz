from typing import Callable
def circular_reference() -> Callable:
    return circular_reference