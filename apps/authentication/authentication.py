from rest_framework import authentication
from rest_framework import exceptions
from .models import MarketplaceCredential
from django.utils import timezone

class MarketplaceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 1. Check for Bearer token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None  # Authentication failed (No header)

        parts = auth_header.split()

        if parts[0].lower() != 'bearer':
            return None  # Authentication failed (Not a Bearer token)

        if len(parts) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        token = parts[1]

        try:
            # 2. Validate the token against the database
            credential = MarketplaceCredential.objects.get(
                access_token=token,
                is_active=True
            )
            
            # 3. Check expiration
            if credential.token_expires_at and credential.token_expires_at < timezone.now():
                raise exceptions.AuthenticationFailed('Token expired')
                
            return (credential.user, credential)
            
        except MarketplaceCredential.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        # We REMOVED the X-Client-ID / X-Client-Secret check here.