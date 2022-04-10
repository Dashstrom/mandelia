from unittest import TestCase
from unittest.mock import patch, PropertyMock
from functools import partial
from mandelia import Controller


ppatch = partial(patch, new_callable=PropertyMock)


class TestController(TestCase):

    def setUp(self):
        pass

    def test_run(self):
        if not Controller.__init__:
            self.fail("No init in Controller")
