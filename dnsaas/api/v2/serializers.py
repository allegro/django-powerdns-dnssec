"""Serializer classes for DNSaaS API"""
import ipaddress

from django.contrib.auth import get_user_model
from powerdns.utils import hostname2domain
from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordRequest,
    RecordTemplate,
    RequestStates,
    Service,
    SuperMaster,
    TsigKey,
)
from rest_framework import serializers
from rest_framework.serializers import (
    PrimaryKeyRelatedField,
    ReadOnlyField,
    ModelSerializer,
    SlugRelatedField,
)


class OwnerSerializer(ModelSerializer):

    owner = SlugRelatedField(
        slug_field='username',
        queryset=get_user_model().objects.all(),
        allow_null=True,
        required=False,
    )


class DomainSerializer(OwnerSerializer):

    id = ReadOnlyField()

    class Meta:
        model = Domain
        read_only_fields = ('notified_serial',)


class ServiceSerializer(ModelSerializer):

    class Meta:
        model = Service


class RecordRequestSerializer(OwnerSerializer):
    last_change = serializers.SerializerMethodField()
    target_owner = SlugRelatedField(
        slug_field='username',
        queryset=get_user_model().objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = RecordRequest

    def get_last_change(self, obj):
        if obj.state == RequestStates.OPEN:
            return obj._get_json_history(obj.get_object())
        else:
            return obj.last_change_json


def _trim_whitespace(data_dict, trim_fields):
    for field_name in trim_fields:
        if field_name not in data_dict:
            continue
        data_dict[field_name] = data_dict[field_name].strip()
    return data_dict


class RecordSerializer(OwnerSerializer):

    class Meta:
        model = Record
        read_only_fields = ('change_date', 'ordername',)

    domain = PrimaryKeyRelatedField(
        queryset=Domain.objects.all(),
        required=False,
        allow_null=True,
    )
    service = PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        required=True,
    )
    service_name = serializers.SerializerMethodField()
    modified = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )
    change_request = serializers.SerializerMethodField(
        'get_change_record_request'
    )
    delete_request = serializers.SerializerMethodField(
        'get_delete_record_request'
    )
    unrestricted_domain = serializers.BooleanField(
        source='domain.unrestricted', read_only=True
    )

    def get_service_name(self, obj):
        return obj.service.name if obj.service else ''

    def get_change_record_request(self, record):
        record_request = record.requests.all()
        if record_request:
            return record_request[0].key
        return None

    def get_delete_record_request(self, record):
        delete_request = record.delete_request.all()
        if delete_request:
            return delete_request[0].key
        return None

    def _clean_txt_content(self, record_type, attrs):
        """
        Remove backslashes form `content` (from `attrs`) inplace when
        `type`=TXT
        """
        # DNS servers don't accept backslashes (\) in content so we neither
        if record_type == 'TXT':
            attrs['content'] = attrs['content'].replace('\\', '')

    def validate(self, attrs):
        _trim_whitespace(attrs, ['name', 'content'])
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

        self._clean_txt_content(record_type, attrs)

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

        if not self.instance:
            # get domain from name only for creation
            if not domain:
                domain = hostname2domain(attrs['name'])
                if not domain:
                    raise serializers.ValidationError({
                        'domain': [
                            'No domain found for name {}'.format(
                                attrs['name']
                            )
                        ]
                    })
                attrs['domain'] = domain
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
