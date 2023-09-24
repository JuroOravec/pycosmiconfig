from typing import Any, Dict, List, Union, TypeVar, Callable, Optional

K = TypeVar("K")
V = TypeVar("V")


def emplace(cache: Dict[K, V], key: K, fn: Callable[[], V]) -> V:
    """@internal"""
    cached = cache.get(key, None)
    if cached is not None:
        return cached
    result = fn()
    cache[key] = result
    return result


def get_property_by_path(source: Dict[str, Any], path: Union[str, List[str]]) -> Any:
    """
    @internal

    Resolves property names or property paths defined with period-delimited
    strings or arrays of strings. Property names that are found on the source
    object are used directly (even if they include a period).

    Nested property names that include periods, within a path, are only
    understood in array paths.
    """
    if isinstance(path, str) and path in source:
        return source[path]

    parsed_path = path.split(".") if isinstance(path, str) else path
    previous = source
    for key in parsed_path:
        if previous is None:
            break
        try:
            previous = previous.get(key, None)
        except AttributeError:
            previous = None
    return previous


def remove_none_values_from_object(
    options: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """@internal"""
    if options is None:
        return None
    return {key: value for key, value in options.items() if value is not None}
