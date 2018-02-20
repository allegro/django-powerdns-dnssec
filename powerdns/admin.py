from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db import models
from django.utils.translation import ugettext_lazy as _

from powerdns.forms import (
    CryptoKeyForm,
    DomainForm,
    DomainMetadataForm,
    RecordForm,
    RecordRequestForm,
)
from powerdns.models import (
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainRequest,
    DomainTemplate,
    Record,
    RecordRequest,
    RecordTemplate,
    Service,
    ServiceOwner,
    SuperMaster,
    TsigKey,
)


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


class DomainOwnerInline(admin.TabularInline):
    model = Domain.direct_owners.through
    extra = 3
    raw_id_fields = ('owner',)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    inlines = [DomainMetadataInline, DomainOwnerInline]
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
    form = DomainForm


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_select_related = ('depends_on', 'domain', 'owner', 'template',)
    list_display = (
        'name',
        'type',
        'content',
        'domain',
        'owner',
        'ttl',
        'prio',
        'formatted_change_date',
    )
    list_filter = ('type', 'ttl', 'auth', 'domain', 'created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name', 'content',)
    readonly_fields = (
        'change_date', 'ordername', 'created', 'modified', 'depends_on',
        'formatted_change_date',
    )
    form = RecordForm


@admin.register(RecordTemplate)
class RecordTemplateAdmin(admin.ModelAdmin):
    list_display = RECORD_LIST_FIELDS


@admin.register(SuperMaster)
class SuperMasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account', 'created', 'modified')
    search_fields = ('ip', 'nameserver',)
    readonly_fields = ('created', 'modified')


@admin.register(DomainMetadata)
class DomainMetadataAdmin(admin.ModelAdmin):
    list_select_related = ('domain',)
    list_display = ('domain', 'kind', 'content',)
    list_filter = ('kind', 'domain', 'created', 'modified')
    list_per_page = 250
    list_filter = ('created', 'modified')
    readonly_fields = ('created', 'modified')
    save_on_top = True
    search_fields = ('content',)
    form = DomainMetadataForm


@admin.register(CryptoKey)
class CryptoKeyAdmin(admin.ModelAdmin):
    list_display = ('domain', 'flags', 'active', 'content',)
    list_filter = ('active', 'domain', 'created', 'modified')
    list_select_related = ('domain',)
    list_per_page = 250
    readonly_fields = ('created', 'modified')
    save_on_top = True
    search_fields = ('content',)
    form = CryptoKeyForm


class RecordTemplateInline(admin.StackedInline):
    model = RecordTemplate
    extra = 1


@admin.register(DomainTemplate)
class DomainTemplateAdmin(admin.ModelAdmin):
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


@admin.register(DeleteRequest)
class DeleteRequestAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    model = DeleteRequest
    list_display = ['content_type', 'state', 'created']
    list_filter = ('content_type', 'state',)
    fields = ['owner', 'target_id', 'content_type', 'state', 'created']
    radio_fields = {'content_type': admin.HORIZONTAL}


@admin.register(DomainRequest)
class DomainRequestAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    model = DomainRequest
    list_display = ['domain', 'state', 'created']
    list_filter = ('state',)
    fields = [
        'domain',
        'key',
        'last_change_json',
        'parent_domain',
        'state',
        'created',
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
    search_fields = ('domain__name',)


@admin.register(RecordRequest)
class RecordRequestAdmin(admin.ModelAdmin):
    model = RecordRequest
    list_display = ['target_' + field for field in RECORD_LIST_FIELDS] + \
                   ['state', 'created']
    list_filter = ('state',)
    readonly_fields = ('created',)
    fields = [
        'domain',
        'key',
        'last_change_json',
        'record',
        'state',
        'created',
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
    search_fields = ('domain__name', 'record__name', 'record__content')
    form = RecordRequestForm


class OwnerInline(admin.TabularInline):
    model = Service.owners.through
    extra = 3
    raw_id_fields = ('owner',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active']
    search_fields = ('name', 'uid',)
    inlines = (OwnerInline,)


@admin.register(ServiceOwner)
class ServiceOwnerAdmin(admin.ModelAdmin):
    list_display = ['owner', 'ownership_type', 'service']
    raw_id_fields = ("service", 'owner')


@admin.register(TsigKey)
class TsigKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'algorithm']
