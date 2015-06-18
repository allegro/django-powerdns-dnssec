import time
import unittest

import DNS
import requests


def get_serial(data):
    """Given dns data returns a serial number"""
    for row in data:
        if isinstance(row, tuple) and len(row) == 2:
            key, value = row
            if key == 'serial':
                return value


class TestSerial(unittest.TestCase):
    """Tests for serial updates"""

    def setUp(self):
        get_domain_request = requests.get(
            'http://dnsaas:8080/api/domains/',
            {'name': 'example.com'}
        )
        domain_url = get_domain_request.json()[0]['url']
        create_record_request = requests.post(
            'http://dnsaas:8080/api/records/',
            {
                'type': 'A',
                'domain': domain_url,
                'name': 'test.example.com',
                'content': '192.168.1.14'
            },
        )
        self.record_url = create_record_request.headers['Location']

    def test_soa_update_on_rm(self):
        """Test if SOA serial is updated on record remove"""

        dns_request = DNS.Request(server='pdns')
        response = dns_request.req(name='example.com')
        old_serial = get_serial(response.authority[0]['data'])
        time.sleep(1)
        requests.delete(self.record_url)
        dns_request = DNS.Request(server='pdns')
        response = dns_request.req(name='example.com')
        new_serial = get_serial(response.authority[0]['data'])
        self.assertGreater(new_serial, old_serial)
