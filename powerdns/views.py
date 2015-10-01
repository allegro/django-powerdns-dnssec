"""Views and viewsets for DNSaaS API"""

from django.views.generic.base import TemplateView

from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordTemplate,
    SuperMaster,
)
from rest_framework.filters import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from powerdns.serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    SuperMasterSerializer,
)
from powerdns.utils import VERSION


class FiltersMixin(object):

    filter_backends = (DjangoFilterBackend,)


class OwnerViewSet(FiltersMixin, ModelViewSet):
    """Base view for objects with owner"""

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.validated_data.get('owner') is None:
            serializer.save(owner=self.request.user)
        else:
            object_ = serializer.save()
            object_.email_owner(self.request.user)


class DomainViewSet(OwnerViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    filter_fields = ('name', 'type')


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_fields = ('name', 'type', 'content', 'domain')


class CryptoKeyViewSet(FiltersMixin, ModelViewSet):

    queryset = CryptoKey.objects.all()
    serializer_class = CryptoKeySerializer
    filter_fields = ('domain',)


class DomainMetadataViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainMetadata.objects.all()
    serializer_class = DomainMetadataSerializer
    filter_fields = ('domain',)


class SuperMasterViewSet(FiltersMixin, ModelViewSet):

    queryset = SuperMaster.objects.all()
    serializer_class = SuperMasterSerializer
    filter_fields = ('ip', 'nameserver')


class DomainTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainTemplate.objects.all()
    serializer_class = DomainTemplateSerializer
    filter_fields = ('name',)


class RecordTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filter_fields = ('domain_template', 'name', 'content')


class HomeView(TemplateView):

    """Homepage. This page should point user to API or admin site. This package
    will provide some minimal homepage template. The administrators of
    DNSaaS solutions are encouraged however to create their own ones."""

    template_name = "powerdns/home.html"

    def get_context_data(self, **kwargs):

        return {
            'version': VERSION,
        }
