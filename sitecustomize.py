"""Test environment shims."""
from __future__ import annotations

# Import the compatibility patches as early as possible so third-party
# libraries such as FastAPI/Pydantic work under Python 3.12 without
# additional dependencies.
from libs.common import compat  # noqa: F401
