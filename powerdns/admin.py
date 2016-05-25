import autocomplete_light
import rules
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import (
    HiddenInput,
    NullBooleanSelect,
    ModelForm,
    ValidationError,
    ModelChoiceField,
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
from powerdns.models.authorisations import Authorisation
from rules.contrib.admin import ObjectPermissionsModelAdmin
from threadlocals.threadlocals import get_current_user


from powerdns.models.templates import (
    DomainTemplate,
    RecordTemplate,
)
from powerdns.models.requests import (
    DeleteRequest,
    DomainRequest,
    RecordRequest,
)
from powerdns.utils import Owned, DomainForRecordValidator, is_owner


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

    def clean_domain(self):
        if (
            self.instance.pk and
            self.instance.domain == self.cleaned_data['domain']
        ):
            # Domain unchanged. Maybe user was assigned the record in a domain
            # She doesn't own.
            return self.cleaned_data['domain']
        validator = DomainForRecordValidator()
        validator.user = self.user
        return validator(self.cleaned_data['domain'])


class CopyingAdmin(admin.ModelAdmin):

    field_prefix = ''
    target_prefix = ''

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        from_pk = request.GET.get(self.from_field)
        if from_pk is not None:
            self.from_object = self.FromModel.objects.get(pk=from_pk)
            for field in self.CopyFieldsModel.copy_fields:
                form.base_fields[field[len(self.field_prefix):]].initial = \
                    getattr(self.from_object, field[len(self.target_prefix):])
        else:
            self.from_object = None
        return form


class RequestAdmin(CopyingAdmin):
    """Admin for domain/record requests"""

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.base_fields['target_owner'].initial =\
            form.base_fields['target_owner'].initial or get_current_user()
        return form


class OwnedAdmin(ForeignKeyAutocompleteAdmin, ObjectPermissionsModelAdmin):
    """Admin for models with owner field"""

    def save_model(self, request, object_, form, change):
        if object_.owner is None:
            object_.owner = request.user
        object_.email_owner(request.user)
        super(OwnedAdmin, self).save_model(request, object_, form, change)

    def get_related_filter(self, model, request):
        return super(OwnedAdmin, self).get_related_filter(model, request)
        user = request.user
        if not issubclass(model, Owned) or rules.is_superuser(user):
            return super(OwnedAdmin, self).get_related_filter(model, request)
        return models.Q(owner=user)


class RecordAdmin(OwnedAdmin, CopyingAdmin):
    form = RecordAdminForm
    list_display = (
        'name',
        'type',
        'content',
        'domain',
        'owner',
        'ttl',
        'prio',
        'change_date',
        'request_change',
        'request_deletion',
    )
    list_display_links = None
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
                'auto_ptr',
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
    FromModel = Domain
    CopyFieldsModel = Domain
    from_field = 'domain'
    field_prefix = 'record_'

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.user = request.user
        return form


class DomainMetadataInline(admin.TabularInline):
    model = DomainMetadata
    extra = 0


class DomainAdmin(OwnedAdmin, CopyingAdmin):
    inlines = [DomainMetadataInline]
    list_display = (
        'name',
        'type',
        'last_check',
        'account',
        'add_record_link',
        'request_change',
        'request_deletion',
    )
    list_display_links = None
    list_filter = _domain_filters + ('created', 'modified')
    list_per_page = 250
    save_on_top = True
    search_fields = ('name',)
    radio_fields = {'type': admin.HORIZONTAL}
    readonly_fields = ('notified_serial', 'created', 'modified')
    FromModel = DomainTemplate
    CopyFieldsModel = DomainTemplate
    from_field = 'template'


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
    list_display = ['name', 'add_domain_link']

RECORD_LIST_FIELDS = (
    'name',
    'type',
    'content',
    'ttl',
    'prio',
)


class RecordTemplateAdmin(ForeignKeyAutocompleteAdmin):
    form = RecordAdminForm
    list_display = RECORD_LIST_FIELDS


class DomainRequestForm(autocomplete_light.forms.ModelForm):
    class Meta:
        exclude = ['owner', 'state']


class DomainRequestAdmin(RequestAdmin):
    form = DomainRequestForm
    list_display = ['domain']
    from_field = 'domain'
    FromModel = Domain
    CopyFieldsModel = DomainRequest
    target_prefix = 'target_'
    readonly_fields = ['key']


class AuthorisationForm(autocomplete_light.forms.ModelForm):
    class Meta:
        model = Authorisation
        fields = [
            'owner',
            'authorised',
            'target',
        ]
        autocomplete_fields = ['authorised', 'target']

    owner = ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=HiddenInput()
    )

    def clean_target(self):
        target = self.cleaned_data['target']
        user = get_current_user()
        if not (user.is_superuser or is_owner(user, target)):
            raise ValidationError(_("You cannot authorize for this"))
        return target


class AuthorisationAdmin(ObjectPermissionsModelAdmin):
    form = AuthorisationForm

    def get_changeform_initial_data(self, request, *args, **kwargs):
        data = super().get_changeform_initial_data(request, *args, **kwargs)
        data['owner'] = request.user
        return data


class DeleteRequestForm(ModelForm):
    class Meta:
        model = DeleteRequest
        fields = [
            'owner',
            'target_id',
            'content_type',
            'key',
        ]
        widgets = {
            'owner': HiddenInput(),
            'key': HiddenInput(),
            'target_id': HiddenInput(),
            'content_type': HiddenInput(),
        }


class DeleteRequestAdmin(ObjectPermissionsModelAdmin):
    form = DeleteRequestForm
    fields = ['owner', 'target_id', 'content_type']

    def add_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['deleted_item'] = str(
            ContentType.objects.get(
                pk=request.GET['content_type']
            ).get_object_for_this_type(pk=request.GET['target_id'])
        )
        return super().add_view(request, extra_context=extra_context)


class RecordRequestForm(autocomplete_light.forms.ModelForm):
    class Meta:
        exclude = ['owner', 'state']


class RecordRequestAdmin(RequestAdmin):
    form = RecordRequestForm
    list_display = ['target_' + field for field in RECORD_LIST_FIELDS]
    from_field = 'record'
    FromModel = Record
    CopyFieldsModel = RecordRequest
    target_prefix = 'target_'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if self.from_object:
            form.base_fields['domain'].initial = self.from_object.domain
        return form

admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
admin.site.register(DomainTemplate, DomainTemplateAdmin)
admin.site.register(RecordTemplate, RecordTemplateAdmin)
admin.site.register(Authorisation, AuthorisationAdmin)
admin.site.register(DomainRequest, DomainRequestAdmin)
admin.site.register(RecordRequest, RecordRequestAdmin)
admin.site.register(DeleteRequest, DeleteRequestAdmin)
