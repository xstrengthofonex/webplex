import unittest

from webplex.route import Route, template_to_regex

class TestRoute(unittest.TestCase):
    def test_template_to_regex_with_static_path(self):
        template = template_to_regex('/a/static/path')
        self.assertEqual(template, "^\/a\/static\/path$")

    def test_template_to_regex_with_dynamic_path(self):
        template = template_to_regex('/{year:\d\d\d\d}/{month:\d\d}/{slug}')
        self.assertEqual(template, '^\/(?P<year>\d\d\d\d)\/(?P<month>\d\d)\/'
            '(?P<slug>[^/]+)$')
