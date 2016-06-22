
import autocomplete_light.shortcuts as al
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from powerdns.utils import VERSION
from powerdns.views import (
    accept_domain_request,
    accept_record_request,
    accept_delete_request,
    obtain_auth_token,
    HomeView,
)
from ui.views import start_page

title = settings.SITE_TITLE
title_v = ' '.join([title, VERSION])

al.autodiscover()

admin.site.site_title = title
admin.site.site_header = title_v
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('dnsaas.api.urls', namespace='api')),
    url(r'^api-token-auth/', obtain_auth_token, name='get-api-token'),
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

if settings.NEW_UI_ENABLED:
    urlpatterns += (
        url(r'^$', start_page, name='home'),
    )
else:
    urlpatterns += (
        url(r'^$', HomeView.as_view()),
        url(r'^ui$', start_page, name='home'),
    )
