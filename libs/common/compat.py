"""Compatibility helpers for third-party libraries."""
from __future__ import annotations

import inspect
from typing import ForwardRef


def _patch_forward_ref_evaluate() -> None:
    """Allow Pydantic v1 to run on Python 3.12.

    Python 3.12 changed :func:`typing.ForwardRef._evaluate` by adding a
    keyword-only ``recursive_guard`` parameter. Pydantic v1 still calls the
    method using the old positional signature which raises ``TypeError``.

    We shim the method so both calling conventions are supported. Once the
    dependency stack is upgraded to versions that natively support Python 3.12
    this patch can be removed.
    """

    signature = inspect.signature(ForwardRef._evaluate)
    parameters = list(signature.parameters.values())

    if not parameters:
        return

    last_param = parameters[-1]
    if last_param.kind is not inspect.Parameter.KEYWORD_ONLY or last_param.name != "recursive_guard":
        return

    original = ForwardRef._evaluate

    def _patched(self, globalns, localns, *args, **kwargs):  # type: ignore[override]
        if (
            len(args) == 1
            and "recursive_guard" not in kwargs
            and "type_params" not in kwargs
        ):
            recursive_guard = args[0]
            return original(self, globalns, localns, None, recursive_guard=recursive_guard)

        return original(self, globalns, localns, *args, **kwargs)

    ForwardRef._evaluate = _patched  # type: ignore[assignment]


_patch_forward_ref_evaluate()

__all__ = ["_patch_forward_ref_evaluate"]
