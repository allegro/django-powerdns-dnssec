# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.db import models
from django.forms import NullBooleanSelect
from django.utils.translation import ugettext_lazy as _
from lck.django.common.admin import ModelAdmin
from powerdns.models import (CryptoKey, Domain, DomainMetadata, Record,
                             SuperMaster)


class NullBooleanRadioSelect(NullBooleanSelect, AdminRadioSelect):
    pass


try:
    from django.contrib.admin import SimpleListFilter
except ImportError:
    _domain_filters = ('type', 'last_check', 'account',)
else:
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
            q = (models.Q(name__endswith='.in-addr.arpa') |
                 models.Q(name__endswith='.ip6.arpa'))
            if self.value() == 'fwd':
                return queryset.exclude(q)
            if self.value() == 'rev':
                return queryset.filter(q)
    _domain_filters = (
        ReverseDomainListFilter, 'type', 'last_check', 'account',
    )


class RecordAdmin(ModelAdmin):
    list_display = (
        'name', 'type', 'content', 'domain', 'ttl', 'prio', 'change_date',
    )
    list_filter = ('type', 'ttl', 'auth', 'domain',)
    list_per_page = 250
    save_on_top = True
    search_fields = ('name', 'content',)
    readonly_fields = ('change_date', 'ordername',)
    related_search_fields = {
        'domain': ['^name'],
    }
    fieldsets = (
        (None, {
            'fields': ('domain', ('type', 'name', 'content',), 'auth',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('prio', 'ttl', 'ordername', 'change_date',)
        }),
    )
    formfield_overrides = {
        models.NullBooleanField: {
            'widget': NullBooleanRadioSelect(
                attrs={'class': 'radiolist inline'}
            ),
        },
    }


class DomainMetadataInline(admin.TabularInline):
    model = DomainMetadata
    extra = 0


class DomainAdmin(ModelAdmin):
    inlines = [DomainMetadataInline]
    list_display = ('name', 'type', 'last_check', 'account',)
    list_filter = _domain_filters
    list_per_page = 250
    save_on_top = True
    search_fields = ('name',)
    radio_fields = {'type': admin.HORIZONTAL}
    readonly_fields = ('notified_serial',)


class SuperMasterAdmin(ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account',)
    search_fields = ('ip', 'nameserver',)


class DomainMetadataAdmin(ModelAdmin):
    list_display = ('domain', 'kind', 'content',)
    list_filter = ('kind', 'domain',)
    list_per_page = 250
    related_search_fields = {
        'domain': ['^name'],
    }
    save_on_top = True
    search_fields = ('content',)


class CryptoKeyAdmin(ModelAdmin):
    list_display = ('domain', 'flags', 'active', 'content',)
    list_filter = ('active', 'domain',)
    list_per_page = 250
    related_search_fields = {
        'domain': ['^name'],
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


admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
