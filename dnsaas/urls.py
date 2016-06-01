
import autocomplete_light.shortcuts as al
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from powerdns.utils import VERSION
from powerdns.views import (
    accept_domain_request,
    accept_record_request,
    accept_delete_request,
    CryptoKeyViewSet,
    DomainMetadataViewSet,
    DomainViewSet,
    HomeView,
    RecordViewSet,
    SuperMasterViewSet,
    DomainTemplateViewSet,
    RecordTemplateViewSet,
    RecordRequestsViewSet,
    TsigKeysViewSet,
)

title = settings.SITE_TITLE
title_v = ' '.join([title, VERSION])

al.autodiscover()

admin.site.site_title = title
admin.site.site_header = title_v
admin.autodiscover()


router = DefaultRouter()
router.register(r'domains', DomainViewSet)
router.register(r'records', RecordViewSet)
router.register(r'crypto-keys', CryptoKeyViewSet)
router.register(r'domains-metadata', DomainMetadataViewSet)
router.register(r'super-masters', SuperMasterViewSet)
router.register(r'domain-templates', DomainTemplateViewSet)
router.register(r'record-templates', RecordTemplateViewSet)
router.register(r'record-requests', RecordRequestsViewSet)
router.register(r'tsigkeys', TsigKeysViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(
        r'^accept-domain/(?P<pk>[0-9]+)$',
        accept_domain_request,
        name='accept_domain'
    ),
    url(
        r'^accept-record/(?P<pk>[0-9]+)$',
        accept_record_request,
        name='accept_record'
    ),
    url(
        r'^accept-delete/(?P<pk>[0-9]+)$',
        accept_delete_request,
        name='accept_delete'
    ),
)
