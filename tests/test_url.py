import unittest
from webplex.router import url, local_request
from webob import Request

class TestUrl(unittest.TestCase):
    def setUp(self):
        local_request.register(Request.blank('http://localhost/'))

    def tearDown(self):
        local_request.unregister()

    def test_url_with_two_segments(self):
        test_url = url('article', 1)
        self.assertEqual(test_url, 'http://localhost/article/1')

    def test_url_with_query(self):
        test_url = url('search', q='some query')
        self.assertEqual(test_url, 'http://localhost/search?q=some+query')