from rest_framework import authentication
from rest_framework import exceptions
from .models import MarketplaceCredential
from django.utils import timezone

class MarketplaceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Try Bearer token authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                credential = MarketplaceCredential.objects.get(
                    access_token=token,
                    is_active=True
                )
                if credential.token_expires_at and credential.token_expires_at < timezone.now():
                    raise exceptions.AuthenticationFailed('Token expired')
                return (credential.user, credential)
            except MarketplaceCredential.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token')

        # Try client_id and client_secret from headers
        client_id = request.META.get('HTTP_X_CLIENT_ID')
        client_secret = request.META.get('HTTP_X_CLIENT_SECRET')

        if client_id and client_secret:
            try:
                credential = MarketplaceCredential.objects.get(
                    client_id=client_id,
                    is_active=True
                )
                if credential.verify_secret(client_secret):
                    return (credential.user, credential)
                else:
                    raise exceptions.AuthenticationFailed('Invalid credentials')
            except MarketplaceCredential.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid client_id')

        return None