from pkg_resources import working_set, Requirement

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from powerdns.views import (
    CryptoKeyViewSet,
    DomainMetadataViewSet,
    DomainViewSet,
    RecordViewSet,
    SuperMasterViewSet,
    DomainTemplateViewSet,
    RecordTemplateViewSet,
)

admin.autodiscover()

title = settings.SITE_TITLE
title_v = ' '.join([
    title,
    working_set.find(Requirement.parse('django-powerdns-dnssec')).version
])

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

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
)
