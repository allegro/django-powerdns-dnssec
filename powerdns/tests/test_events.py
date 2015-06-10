# -*- encoding: utf-8 -*-


from powerdns.models import Record
from powerdns.tests.utils import RecordTestCase, RecordFactory


class TestSOASerialUpdate(RecordTestCase):

    def setUp(self):
        super(TestSOASerialUpdate, self).setUp()
        self.soa_record = RecordFactory(
            domain=self.domain,
            type='SOA',
            name='example.com',
            content=(
                'na1.example.com. hostmaster.example.com. '
                '0 43200 600 1209600 600'
            ),
        )
        # Less than 1 second will elapse until the test runs, so we update
        # this manually while circumventing save()
        Record.objects.filter(pk=self.soa_record.pk).update(
            change_date=1432720132
        )
        self.a_record = RecordFactory(
            domain=self.domain,
            type='A',
            name='www.example.com',
            content='192.168.1.1',
        )
        self.cname_record = RecordFactory(
            domain=self.domain,
            type='CNAME',
            name='blog.example.com',
            content='www.example.com',
        )

    def test_soa_update(self):
        """Test if SOA change_date is updated when a record is removed"""
        old_serial = Record.objects.get(pk=self.soa_record.pk).change_date
        self.a_record.delete()
        new_serial = Record.objects.get(pk=self.soa_record.pk).change_date
        self.assertGreater(new_serial, old_serial)
