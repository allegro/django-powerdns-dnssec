from django.conf.urls import include, url

from powerdns.utils import patterns


urlpatterns = patterns(
    '',
    url(r'', include('dnsaas.api.v1.urls', namespace='default')),
    url(r'^v2/', include('dnsaas.api.v2.urls', namespace='v2')),
)
