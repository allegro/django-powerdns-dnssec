from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.db import models
from django.forms import NullBooleanSelect, ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from powerdns.models.powerdns import (
    CryptoKey,
    Domain,
    DomainMetadata,
    Record,
    SuperMaster,
)

from powerdns.models.templates import (
    DomainTemplate,
    RecordTemplate,
)


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


class RecordAdminForm(ModelForm):
    def clean_type(self):
        type = self.cleaned_data['type']
        if not type:
            raise ValidationError(_("Record type is required"))
        return type


class OwnedAdmin(admin.ModelAdmin):
    """Admin for models with owner field"""
    def save_model(self, request, object_, form, change):
        if object_.owner is None:
            object_.owner = request.user
        object_.email_owner(request.user)
        super(OwnedAdmin, self).save_model(request, object_, form, change)


class RecordAdmin(ForeignKeyAutocompleteAdmin, OwnedAdmin):
    form = RecordAdminForm
    list_display = (
        'name', 'type', 'content', 'domain', 'ttl', 'prio', 'change_date',
    )
    list_filter = ('type', 'ttl', 'auth', 'domain', 'created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name', 'content',)
    readonly_fields = ('change_date', 'ordername', 'created', 'modified')
    related_search_fields = {
        'domain': ('name',),
    }
    fieldsets = (
        (None, {
            'fields': (
                'owner',
                'domain',
                ('type', 'name', 'content',),
                'auth',
            ),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('prio', 'ttl', 'ordername', 'change_date',)
        }),
        (None, {'fields': ('created', 'modified')})
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


class DomainAdmin(OwnedAdmin):
    inlines = [DomainMetadataInline]
    list_display = ('name', 'type', 'last_check', 'account',)
    list_filter = _domain_filters + ('created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name',)
    radio_fields = {'type': admin.HORIZONTAL}
    readonly_fields = ('notified_serial', 'created', 'modified')


class SuperMasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account', 'created', 'modified')
    search_fields = ('ip', 'nameserver',)
    readonly_fields = ('created', 'modified')


class DomainMetadataAdmin(ForeignKeyAutocompleteAdmin):
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


class RecordTemplateAdmin(ForeignKeyAutocompleteAdmin):
    form = RecordAdminForm
    list_display = (
        'name',
        'type',
        'content',
        'domain_template',
        'ttl',
        'prio',
    )


admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
admin.site.register(DomainTemplate, DomainTemplateAdmin)
admin.site.register(RecordTemplate, RecordTemplateAdmin)
