"""Views and viewsets for DNSaaS API"""
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from powerdns.models import (
    DeleteRequest,
    DomainRequest,
    RecordRequest,
)

from powerdns.utils import VERSION


log = logging.getLogger(__name__)


class ObtainAuthToken(ObtainAuthToken):
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'token': token.key,
            'user': user.get_full_name() or user.username,
        })
obtain_auth_token = ObtainAuthToken.as_view()


class HomeView(TemplateView):

    """
    Homepage. This page should point user to API or admin site. This package
    will provide some minimal homepage template. The administrators of
    DNSaaS solutions are encouraged however to create their own ones.
    """

    template_name = "powerdns/home.html"

    def get_context_data(self, **kwargs):

        return {
            'version': VERSION,
        }


def accept_request_factory(request_model, model_name=None):
    def result(request, pk):
        request = request_model.objects.get(pk=pk)
        domain = request.accept()
        if model_name:
            return redirect(
                reverse(
                    'admin:powerdns_{}_change'.format(model_name),
                    args=(domain.pk,)
                )
            )
        else:
            return redirect(reverse('admin:index'))
    return result

accept_domain_request = accept_request_factory(DomainRequest, 'domain')
accept_record_request = accept_request_factory(RecordRequest, 'record')
accept_delete_request = accept_request_factory(DeleteRequest)
