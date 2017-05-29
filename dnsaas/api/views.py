from django.core.urlresolvers import reverse
from django.http import HttpResponse


def api_not_available(request):
    html = """
        <html><body>
            API v1 was removed. Please use new API v2, available at:
            <a href="{url}">{url}</a>
        </body></html>
    """.format(url=reverse('api:v2:api-root'))
    return HttpResponse(html)
