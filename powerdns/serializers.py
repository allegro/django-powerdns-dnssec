"""Serializer classes for DNSaaS API"""

from django.contrib.auth.models import User
from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordTemplate,
    SuperMaster,
)
from rest_framework.serializers import(
    HyperlinkedModelSerializer,
    HyperlinkedRelatedField,
    SlugRelatedField,
    ReadOnlyField,
)
from powerdns.utils import DomainForRecordValidator
from powerdns.models.tsigkeys import TsigKeys


class OwnerSerializer(HyperlinkedModelSerializer):

    owner = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )


class DomainSerializer(OwnerSerializer):

    id = ReadOnlyField()

    class Meta:
        model = Domain
        read_only_fields = ('notified_serial',)


class RecordSerializer(OwnerSerializer):

    id = ReadOnlyField()

    class Meta:
        model = Record
        read_only_fields = ('change_date', 'ordername',)

    domain = HyperlinkedRelatedField(
        queryset=Domain.objects.all(),
        view_name='domain-detail',
        validators=[DomainForRecordValidator()],
    )


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


class TsigKeysTemplateSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = TsigKeys
