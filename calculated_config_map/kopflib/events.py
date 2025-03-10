# Explicit event posting using kopf. This works even when log posting is disabled

import typing

from kopf._core.engines import posting
from kopf._cogs.structs import bodies
from kopf._cogs.structs import dicts


# taken from kopf._core.engines.posting
def event(
    objs: bodies.Body | typing.Iterable[bodies.Body],
    *,
    type: str,
    reason: str,
    message: str = "",
) -> None:
    for obj in typing.cast(typing.Iterator[bodies.Body], dicts.walk(objs)):
        ref = bodies.build_object_reference(obj)
        posting.enqueue(ref=ref, type=type, reason=reason, message=message)


def info(
    objs: bodies.Body | typing.Iterable[bodies.Body],
    *,
    reason: str,
    message: str = "",
) -> None:
    event(objs, type="Normal", reason=reason, message=message)


def warn(
    objs: bodies.Body | typing.Iterable[bodies.Body],
    *,
    reason: str,
    message: str = "",
) -> None:
    event(objs, type="Warning", reason=reason, message=message)


def error(
    objs: bodies.Body | typing.Iterable[bodies.Body],
    *,
    reason: str,
    message: str = "",
) -> None:
    event(objs, type="Error", reason=reason, message=message)
