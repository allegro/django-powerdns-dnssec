"""Serializer classes for DNSaaS API"""
import ipaddress

from django.contrib.auth.models import User
from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordRequest,
    RecordTemplate,
    SuperMaster,
)
from rest_framework.serializers import(
    HyperlinkedModelSerializer,
    HyperlinkedRelatedField,
    SlugRelatedField,
    ReadOnlyField,
    ValidationError,
)
from powerdns.utils import DomainForRecordValidator
from powerdns.models.tsigkeys import TsigKey


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


class RecordRequestSerializer(OwnerSerializer):

    id = ReadOnlyField()
    target_owner = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = RecordRequest


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


class RecordSerializerV2(RecordSerializer):
    domain = HyperlinkedRelatedField(
        queryset=Domain.objects.all(),
        view_name='domain-detail',
    )

    def validate(self, attrs):
        domain, content, record_type = (
            attrs.get('domain'), attrs.get('content'), attrs.get('type')
        )
        if (
            domain and domain.template and
            domain.template.is_public_domain and
            content and record_type == 'A'
        ):
            address = ipaddress.ip_address(content)
            if address.is_private:
                raise ValidationError('IP address can not be private.')

        return attrs


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
        model = TsigKey
