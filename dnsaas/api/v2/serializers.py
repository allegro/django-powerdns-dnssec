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
from rest_framework import serializers
from rest_framework.serializers import(
    PrimaryKeyRelatedField,
    ReadOnlyField,
    ModelSerializer,
    SlugRelatedField,
)
from powerdns.models.tsigkeys import TsigKey


class OwnerSerializer(ModelSerializer):

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
    target_owner = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = RecordRequest


class RecordSerializer(OwnerSerializer):

    class Meta:
        model = Record
        read_only_fields = ('change_date', 'ordername',)

    domain = PrimaryKeyRelatedField(
        queryset=Domain.objects.all(),
    )

    def validate(self, attrs):
        domain, content, record_type = (
            attrs.get('domain'), attrs.get('content'), attrs.get('type')
        )

        if (
            record_type == 'A'
        ):
            try:
                ipaddress.ip_address(content)
            except ValueError:
                raise serializers.ValidationError(
                    {'content':
                     ['Content should be IP valid address when type="A".']}
                )

        if (
            domain and domain.template and
            domain.template.is_public_domain and
            content and record_type == 'A'
        ):
            address = ipaddress.ip_address(content)
            if address.is_private:
                raise serializers.ValidationError(
                    {'content': ['IP address cannot be private.']}
                )

        return attrs


class CryptoKeySerializer(ModelSerializer):

    class Meta:
        model = CryptoKey


class DomainMetadataSerializer(ModelSerializer):

    class Meta:
        model = DomainMetadata


class SuperMasterSerializer(ModelSerializer):

    class Meta:
        model = SuperMaster


class DomainTemplateSerializer(ModelSerializer):

    class Meta:
        model = DomainTemplate


class RecordTemplateSerializer(ModelSerializer):

    class Meta:
        model = RecordTemplate


class TsigKeysTemplateSerializer(ModelSerializer):

    class Meta:
        model = TsigKey
