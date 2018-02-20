from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from dal import autocomplete
from dnsaas.utils import VERSION
from powerdns.models import (
    Domain,
    Record,
    Service,
)
from powerdns.utils import patterns
from powerdns.views import obtain_auth_token
from ui.views import start_page


title = settings.SITE_TITLE
title_v = ' '.join([title, VERSION])

admin.site.site_title = title
admin.site.site_header = title_v
admin.autodiscover()


autocomplete_urlpatterns = [
    url(
        'users/$',
        staff_member_required(
            autocomplete.Select2QuerySetView.as_view(model=get_user_model())
        ),
        name='users',
    ),
    url(
        'domains/$',
        staff_member_required(
            autocomplete.Select2QuerySetView.as_view(model=Domain)
        ),
        name='domains',
    ),
    url(
        'records/$',
        staff_member_required(
            autocomplete.Select2QuerySetView.as_view(model=Record)
        ),
        name='records',
    ),
    url(
        'services/$',
        staff_member_required(
            autocomplete.Select2QuerySetView.as_view(model=Service)
        ),
        name='services',
    ),
]


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^autocomplete/',
        include(autocomplete_urlpatterns, namespace='autocomplete')
    ),
    url(r'^api/', include('dnsaas.api.urls', namespace='api')),
    url(r'^api-token-auth/', obtain_auth_token, name='get-api-token'),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url(r'^$', start_page, name='home'),
)
