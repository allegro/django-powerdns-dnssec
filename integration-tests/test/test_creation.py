import DNS
from DNS.Type import PTR

from .util import TestBase


class TestCreation(TestBase):
    """Tests for domain and record creation"""

    def setUp(self):
        domain_create_rq = self.post(
            'http://dnsaas:8080/api/domains/', {
                'name': 'example2.com',
                'template': 'http://dnsaas:8080/api/domain-templates/1/',
            }
        )
        print(domain_create_rq.status_code)
        print(domain_create_rq.text)
        self.domain_url = domain_create_rq.headers['Location']
        record_create_rq = self.post(
            'http://dnsaas:8080/api/records/', data={
                'type': 'A',
                'name': 'www.example2.com',
                'content': '192.168.2.11',
                'auto_ptr': '1',
                'domain': self.domain_url,
            }
        )
        self.record_url = record_create_rq.headers['Location']

    def test_ptr_exists(self):
        """Test if PTR is created for the A record"""

        request = DNS.Request(server='pdns')
        response = request.req('11.2.168.192.in-addr.arpa', qtype=PTR)
        self.assertEqual(len(response.answers), 1)

    def tearDown(self):
        self.delete(self.domain_url)
