from dal import autocomplete
from django import forms

from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    Record,
    RecordRequest,
)


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = (
            'owner', 'service', 'domain', 'name', 'type', 'content', 'ttl',
            'prio', 'auth', 'disabled', 'remarks', 'template',
        )
        widgets = {
            'owner': autocomplete.ModelSelect2(
                url='autocomplete:users'
            ),
            'domain': autocomplete.ModelSelect2(
                url='autocomplete:domains'
            ),
            'service': autocomplete.ModelSelect2(
                url='autocomplete:services'
            ),
        }


class RecordRequestForm(forms.ModelForm):
    class Meta:
        model = RecordRequest
        fields = (
            'domain', 'key', 'last_change_json', 'record', 'state',
            'target_auth', 'target_content', 'target_disabled', 'target_name',
            'owner', 'target_prio', 'target_remarks', 'target_ttl',
            'target_type',
        )
        widgets = {
            'target_owner': autocomplete.ModelSelect2(
                url='autocomplete:users'
            ),
            'domain': autocomplete.ModelSelect2(
                url='autocomplete:domains'
            ),
            'record': autocomplete.ModelSelect2(
                url='autocomplete:records'
            ),
        }


class DomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = (
            'owner', 'service', 'name', 'master', 'last_check', 'type',
            'account', 'remarks', 'template', 'reverse_template', 'auto_ptr',
            'unrestricted', 'require_sec_acceptance', 'require_seo_acceptance',
        )
        widgets = {
            'owner': autocomplete.ModelSelect2(
                url='autocomplete:users'
            ),
            'service': autocomplete.ModelSelect2(
                url='autocomplete:services'
            ),
        }


class DomainMetadataForm(forms.ModelForm):
    class Meta:
        model = DomainMetadata
        fields = ('domain', 'kind', 'content')
        widgets = {
            'domain': autocomplete.ModelSelect2(
                url='autocomplete:domains'
            )
        }


class CryptoKeyForm(forms.ModelForm):
    class Meta:
        model = CryptoKey
        fields = ('domain', 'flags', 'active', 'content',)
        widgets = {
            'domain': autocomplete.ModelSelect2(
                url='autocomplete:domains'
            )
        }
