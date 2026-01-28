from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import MarketplaceCredential
from django.core.management import call_command

@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    client_id = request.data.get('client_id')
    client_secret = request.data.get('client_secret')

    if not client_id or not client_secret:
        return Response(
            {'error': 'client_id and client_secret required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        credential = MarketplaceCredential.objects.get(
            client_id=client_id,
            is_active=True
        )
        if credential.verify_secret(client_secret):
            token = credential.generate_access_token()
            return Response({
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': 86400,
                'marketplace': credential.marketplace
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except MarketplaceCredential.DoesNotExist:
        return Response(
            {'error': 'Invalid client_id'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_credentials(request):
    username = request.data.get('username')
    password = request.data.get('password')
    marketplace = request.data.get('marketplace')

    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if marketplace not in ['AMAZON_AE', 'NOON_AE']:
        return Response(
            {'error': 'Invalid marketplace'},
            status=status.HTTP_400_BAD_REQUEST
        )

    credential, created = MarketplaceCredential.objects.get_or_create(
        user=user,
        marketplace=marketplace
    )

    if created or not credential.client_id:
        credential.generate_credentials()

    return Response({
        'client_id': credential.client_id,
        'client_secret': credential.client_secret,
        'marketplace': credential.marketplace
    })
@api_view(['GET'])
@permission_classes([AllowAny])
def emergency_setup(request):
    try:
        # 1. Run Migrations
        call_command('migrate', interactive=False)
        
        # 2. Create Test User
        user, _ = User.objects.get_or_create(username='testuser')
        user.set_password('testpass123')
        user.save()
        
        # 3. Create Amazon Credentials (Matching your docs)
        amz, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='AMAZON_AE')
        amz.client_id = "amazon_ae_yVkOidNBLFFQ0Lum0RhYSg"
        amz.client_secret = "ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
        amz.save()
        
        # 4. Create Noon Credentials (Matching your docs)
        noon, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='NOON_AE')
        noon.client_id = "noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw"
        noon_secret = "Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"
        noon.client_secret = noon_secret
        noon.save()

        return Response({
            "status": "success",
            "message": "Database migrated and credentials created!",
            "credentials": "Use the ones from your documentation."
        })
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)