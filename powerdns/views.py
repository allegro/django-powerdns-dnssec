"""Views and viewsets for DNSaaS API"""
import logging

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response


log = logging.getLogger(__name__)


class ObtainAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'token': token.key,
            'user': user.get_full_name() or user.username,
            'is_admin': user.is_superuser
        })
obtain_auth_token = ObtainAuthToken.as_view()
