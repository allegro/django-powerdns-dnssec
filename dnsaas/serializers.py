"""Serializer classes for DNSaaS API"""

from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordTemplate,
    SuperMaster,
)
from rest_framework.serializers import HyperlinkedModelSerializer


class DomainSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Domain
        read_only_fields = ('notified_serial',)


class RecordSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Record
        read_only_fields = ('change_date', 'ordername',)


class CryptoKeySerializer(HyperlinkedModelSerializer):

    class Meta:
        model = CryptoKey


class DomainMetadataSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = DomainMetadata


class SuperMasterSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = SuperMaster


class DomainTemplateSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = DomainTemplate


class RecordTemplateSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = RecordTemplate
