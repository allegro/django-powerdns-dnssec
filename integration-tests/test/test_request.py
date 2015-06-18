import unittest
import DNS


class TestRequest(unittest.TestCase):

    def test_example(self):
        request = DNS.Request()
        response = request.req(name='www.example.com', server='pdns')
        self.assertEqual(len(response.answers), 1)
        self.assertEqual(response.answers[0]['data'], '192.168.1.11')
