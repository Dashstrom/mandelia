""""Test importing specific modules."""
import sys
from unittest import TestCase


class TestImport(TestCase):

    def test_import_paramspec(self) -> None:
        # pylint: disable=import-outside-toplevel, unused-import
        if sys.version_info >= (3, 10):
            from typing import ParamSpec
        else:
            from typing_extensions import ParamSpec  # noqa: F401
        if not callable(ParamSpec):  # type: ignore
            self.fail("Invalid ParamSpec")
