from rest_framework import authentication
from rest_framework import exceptions
from .models import MarketplaceCredential
from django.utils import timezone

class MarketplaceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

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