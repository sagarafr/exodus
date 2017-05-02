from web_site.foo.tests.functional import FunctionalTest
from web_site.foo.extensions import cel


class TestEnvironment(FunctionalTest):

    def test_celerybeat_schedule(self):
        for task in cel.conf['CELERYBEAT_SCHEDULE'].values():
            self.assertIn(task['task'], cel.tasks)
