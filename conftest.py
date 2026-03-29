"""
Root-level conftest.py — runs before any test collection.

Python 3.14 is incompatible with the C extensions in protobuf 4.x
(google._upb._message uses metaclasses with custom tp_new).
Stubbing google.generativeai here — before any module-level import
executes — lets the test suite mock it cleanly in individual tests.
"""
import sys
import types
from unittest.mock import MagicMock

# Only stub if the real import would fail (i.e. not already loaded cleanly).
if "google.generativeai" not in sys.modules:
    _genai_stub = MagicMock()
    _genai_stub.__name__ = "google.generativeai"
    sys.modules["google.generativeai"] = _genai_stub
    # Also stub sub-modules that pipeline.py references
    sys.modules["google.generativeai.types"] = MagicMock()
