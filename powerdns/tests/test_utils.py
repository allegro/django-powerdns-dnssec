from django.test import TestCase

from powerdns.utils import to_reverse, reverse_pointer


class TestReversing(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ipv4 = '192.168.1.2'
        cls.ipv6 = '2001:0db8:0:0::1428:57ab'

    def test_reversing_pointer_ipv4(self):
        rev = reverse_pointer(self.ipv4)
        self.assertEqual(rev, '2.1.168.192.in-addr.arpa')

    def test_reversing_pointer_ipv6(self):
        rev = reverse_pointer(self.ipv6)
        self.assertEqual(
            rev, 'b.a.7.5.8.2.4.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'  # noqa
        )

    def test_to_reverse_ipv4(self):
        last_byte, domain = to_reverse(self.ipv4)
        self.assertEqual(domain, '1.168.192.in-addr.arpa')
        self.assertEqual(last_byte, '2')

    def test_to_reverse_ipv6(self):
        last_byte, domain = to_reverse(self.ipv6)
        self.assertEqual(domain, 'a.7.5.8.2.4.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa')  # noqa
        self.assertEqual(last_byte, 'b')
