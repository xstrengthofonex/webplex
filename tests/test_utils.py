import unittest
from webob import Request

from webplex.utils import clean_path, path_match, strip_host_port

class TestUtils(unittest.TestCase):
    def test_clean_path_with_dot_paths(self):
        self.assertEqual(clean_path("/"), "/")
        self.assertEqual(clean_path("///"), "/")
        self.assertEqual(clean_path("///foo/.//bar//"), "/foo/bar/")
        self.assertEqual(clean_path("///foo/.//bar//.//..//.//baz"), "/foo/baz")
        self.assertEqual(clean_path("///..//./foo/.//bar"), "/foo/bar")

    def test_clean_path_with_two_slashes(self):
        self.assertEqual(clean_path("//"), "/")

    def test_clean_path_with_empty_string(self):
        self.assertEqual(clean_path(""), "/")

    def test_clean_path_with_trailing_backslash(self):
        self.assertEqual(clean_path('/foo/'), '/foo/')

    def test_path_match_with_pattern_of_length_zero(self):
        self.assertFalse(path_match("", "/"))

    def test_path_match_matching_pattern_and_path(self):
        self.assertTrue(path_match('/foo', '/foo'))

    def test_strip_host_port_with_no_port(self):
        self.assertEqual(strip_host_port("localhost"), "localhost")

    def test_strip_host_port_with_port(self):
        self.assertEqual(strip_host_port("localhost:8080"), "localhost")



