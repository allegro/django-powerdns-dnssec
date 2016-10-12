from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.forms import NullBooleanSelect
from powerdns.models.requests import (
    DeleteRequest,
    DomainRequest,
    RecordRequest,
)
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin

from powerdns.models.powerdns import (
    CryptoKey,
    Domain,
    DomainMetadata,
    Record,
    SuperMaster,
)
from powerdns.models.ownership import Service, ServiceOwner
from powerdns.models.templates import (
    DomainTemplate,
    RecordTemplate,
)
from powerdns.models.tsigkeys import TsigKey


RECORD_LIST_FIELDS = (
    'name',
    'type',
    'content',
    'ttl',
    'prio',
)


class ReverseDomainListFilter(SimpleListFilter):
    title = _('domain class')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'domain_class'

    def lookups(self, request, model_admin):
        return (
            ('fwd', _('domain:forward')),
            ('rev', _('domain:reverse')),
        )

    def queryset(self, request, queryset):
        q = (
            models.Q(name__endswith='.in-addr.arpa') |
            models.Q(name__endswith='.ip6.arpa')
        )
        if self.value() == 'fwd':
            return queryset.exclude(q)
        if self.value() == 'rev':
            return queryset.filter(q)
        return queryset


class DomainMetadataInline(admin.TabularInline):
    model = DomainMetadata
    extra = 0


class DomainAdmin(ForeignKeyAutocompleteAdmin, admin.ModelAdmin):
    inlines = [DomainMetadataInline]
    list_display = (
        'name',
        'type',
        'last_check',
        'account',
    )
    list_filter = (
        ReverseDomainListFilter, 'type', 'last_check', 'account', 'created',
        'modified'
    )
    list_per_page = 250
    save_on_top = True
    search_fields = ('name',)
    radio_fields = {'type': admin.HORIZONTAL}
    readonly_fields = ('notified_serial', 'created', 'modified')


class NullBooleanRadioSelect(NullBooleanSelect, AdminRadioSelect):
    pass


class RecordAdmin(ForeignKeyAutocompleteAdmin, admin.ModelAdmin):
    list_select_related = ('depends_on', 'domain', 'owner', 'template',)
    list_display = (
        'name',
        'type',
        'content',
        'domain',
        'owner',
        'ttl',
        'prio',
        'change_date',
    )
    list_filter = ('type', 'ttl', 'auth', 'domain', 'created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name', 'content',)
    readonly_fields = (
        'change_date', 'ordername', 'created', 'modified', 'depends_on',
    )
    related_search_fields = {
        'domain': ('name',),
    }
    formfield_overrides = {
        models.NullBooleanField: {
            'widget': NullBooleanRadioSelect(
                attrs={'class': 'radiolist inline'}
            ),
        },
    }


class RecordTemplateAdmin(ForeignKeyAutocompleteAdmin):
    list_display = RECORD_LIST_FIELDS


class SuperMasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account', 'created', 'modified')
    search_fields = ('ip', 'nameserver',)
    readonly_fields = ('created', 'modified')


class DomainMetadataAdmin(ForeignKeyAutocompleteAdmin):
    list_select_related = ('domain',)
    list_display = ('domain', 'kind', 'content',)
    list_filter = ('kind', 'domain', 'created', 'modified')
    list_per_page = 250
    list_filter = ('created', 'modified')
    readonly_fields = ('created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    save_on_top = True
    search_fields = ('content',)


class CryptoKeyAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('domain', 'flags', 'active', 'content',)
    list_filter = ('active', 'domain', 'created', 'modified')
    list_select_related = ('domain',)
    list_per_page = 250
    readonly_fields = ('created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    save_on_top = True
    search_fields = ('content',)
    formfield_overrides = {
        models.NullBooleanField: {
            'widget': NullBooleanRadioSelect(
                attrs={'class': 'radiolist inline'}
            ),
        },
    }


class RecordTemplateInline(admin.StackedInline):
    model = RecordTemplate
    extra = 1


class DomainTemplateAdmin(ForeignKeyAutocompleteAdmin):
    inlines = [RecordTemplateInline]
    list_display = ['name', 'is_public_domain']


class ReadonlyAdminMixin(object):
    def get_readonly_fields(self, request, obj=None):
        ro_fields = (
            self.fields if not self.readonly_fields else self.readonly_fields
        )
        return ro_fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DeleteRequestAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    model = DeleteRequest
    fields = ['owner', 'target_id', 'content_type']


class DomainRequestAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    model = DomainRequest
    list_display = ['domain']
    fields = [
        'domain',
        'key',
        'last_change_json',
        'parent_domain',
        'state',
        'target_account',
        'target_auto_ptr',
        'target_master',
        'target_name',
        'target_owner',
        'target_remarks',
        'target_reverse_template',
        'target_template',
        'target_type',
        'target_unrestricted',
    ]


class RecordRequestAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    model = RecordRequest
    list_display = ['target_' + field for field in RECORD_LIST_FIELDS]
    fields = [
        'domain',
        'key',
        'last_change_json',
        'record',
        'state',
        'target_auth',
        'target_content',
        'target_disabled',
        'target_name',
        'target_owner',
        'target_prio',
        'target_remarks',
        'target_ttl',
        'target_type',
    ]


class OwnerInline(admin.TabularInline):
    model = Service.owners.through
    extra = 3
    raw_id_fields = ('user',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = (OwnerInline,)


@admin.register(ServiceOwner)
class ServiceOwnerAdmin(admin.ModelAdmin):
    raw_id_fields = ("service", 'user')


# walkaround long load of user change_view until autocomplete-light3 gets
# integrated
UserAdmin.filter_horizontal = ()
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(RecordTemplate, RecordTemplateAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
admin.site.register(TsigKey)
admin.site.register(DomainTemplate, DomainTemplateAdmin)
admin.site.register(DomainRequest, DomainRequestAdmin)
admin.site.register(RecordRequest, RecordRequestAdmin)
admin.site.register(DeleteRequest, DeleteRequestAdmin)
