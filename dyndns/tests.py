from django.test import TestCase
from django.test.client import Client
import re

class SimpleTest(TestCase):
    def test_basic_update(self):
        """
        Test that update works
        """
	c = Client()
	response = c.get(r"/dyndns/?hostname=your.hostname.com&myip=1.1.1.1")
        # Check that the HTTP response is 200 OK.
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(re.search('good', response.content), 'Test failed!')
    def test_invalid_ip_update(self):
        """
        Test that update works
        """
	c = Client()
	response = c.get(r"/dyndns/?hostname=your.hostname.com&myip=NOTANIP")
        # Check that the HTTP response is 200 OK.
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(re.search('notfqdn', response.content), 'Test failed!')

