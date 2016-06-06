import re

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse


def get_api_version(request):
    """Gets api version from header"""
    value = request.META.get('HTTP_ACCEPT', '')
    version = re.findall(r'v\d+', value, re.IGNORECASE)
    version = version[0] if version else None
    return version


class VersionSwitch(object):
    """
    Translates API urls from AcceptHeaderVersioning to NamespaceVersioning

    This allows API users to specify API version both, by:
        - url, like '/api/v2/records',
        - header, like '/api/records' + header:
            'HTTP_ACCEPT': 'application/json; version=v2'
    """
    def process_request(self, request):
        url = resolve(request.path_info)
        api_version = get_api_version(request)
        if url.namespace.startswith('api:') and api_version:
            url_version = url.namespace.split(':')[-1]
            request.path_info = reverse(
                '{}:{}'.format(
                    url.namespace.replace(url_version, api_version),
                    url.url_name,
                ),
                args=url.args,
                kwargs=url.kwargs
            )
