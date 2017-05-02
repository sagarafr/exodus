import unittest

from . import FunctionalTest
from web_site.foo.commands.generate_schema import GenerateSchema


class TestGenerateSchema(FunctionalTest):

    def test_generate_schema(self):
        gs = GenerateSchema(self.app)
        gs.run('/paas/person', '/v6')
