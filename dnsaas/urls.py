from django.conf.urls import patterns, include, url
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
from powerdns.admin import admin_site


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
    url(r'^admin/', include(admin_site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
)
