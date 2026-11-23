"""Read cache for derived values (package 23 B, D25). Derived values stay derived on read: this only remembers the
result of a pure function of ONE character object while that object lives. Nothing is ever stored in the data.

- @cached: the first argument is the Character (immutable: the same object always gives the same result); the key
  also holds the other arguments (strings / numbers as they are, objects by identity, kept alive with the entry) and
  the current rule-constant scope (rules.using), so a value computed under other overrides is never reused.
- clear(): drops everything; dispatch() calls it at every command (a cache never survives a command).
- disabled(): a scope where nothing is cached (tests compare cached and uncached results).
"""
import contextlib
import functools
import weakref

from wp.rules_data import rules as rd

_STORE = {}            # id(character) -> {key: (kept objects, value)}
_ON = [True]
_PLAIN = (str, int, float, bool, type(None))


def clear():
    _STORE.clear()


@contextlib.contextmanager
def disabled():
    _ON[0] = False
    try:
        yield
    finally:
        _ON[0] = True


def _hashable(v):
    if isinstance(v, dict):
        return tuple(sorted((k, _hashable(x)) for k, x in v.items()))
    if isinstance(v, (list, tuple)):
        return tuple(_hashable(x) for x in v)
    return v


def _scope_key():
    scope = rd._SCOPE.get()
    return _hashable(scope) if scope else ()


def _arg_key(a):
    if isinstance(a, _PLAIN):
        return a, None
    if isinstance(a, tuple) and all(isinstance(x, _PLAIN) for x in a):
        return a, None
    return ("@id", id(a)), a


def _forget(cid):
    _STORE.pop(cid, None)


def cached(fn):
    name = fn.__module__ + "." + fn.__qualname__

    @functools.wraps(fn)
    def wrapper(ch, *args, **kwargs):
        if not _ON[0] or kwargs:
            return fn(ch, *args, **kwargs)
        parts, kept = [], []
        for a in args:
            k, obj = _arg_key(a)
            parts.append(k)
            if obj is not None:
                kept.append(obj)
        try:
            key = (name, tuple(parts), _scope_key())
        except TypeError:                  # an unhashable override value: no cache
            return fn(ch, *args)
        cid = id(ch)
        box = _STORE.get(cid)
        if box is None:
            box = _STORE[cid] = {}
            try:
                weakref.finalize(ch, _forget, cid)
            except TypeError:
                pass
        hit = box.get(key)
        if hit is not None and all(x is y for x, y in zip(hit[0], kept)):
            return hit[1]
        value = fn(ch, *args)
        box[key] = (tuple(kept), value)
        return value
    return wrapper
