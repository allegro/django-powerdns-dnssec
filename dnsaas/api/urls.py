from django.conf.urls import include, url

from dnsaas.api import views
from powerdns.utils import patterns


urlpatterns = patterns(
    '',
    url(r'^v2/', include('dnsaas.api.v2.urls', namespace='v2')),
    url(r'', views.api_not_available, name='api_not_available'),
)
