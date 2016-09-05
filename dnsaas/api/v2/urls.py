from django.conf.urls import url, patterns

from rest_framework.routers import DefaultRouter

from .views import (
    CryptoKeyViewSet,
    DomainMetadataViewSet,
    DomainViewSet,
    RecordViewSet,
    SuperMasterViewSet,
    DomainTemplateViewSet,
    RecordTemplateViewSet,
    RecordRequestsViewSet,
    TsigKeysViewSet,
    IPRecordView,
)

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
urlpatterns = router.urls
urlpatterns += patterns(
    '',
    url(r'^ip_record/', IPRecordView.as_view(), name='ip-record'),
)
