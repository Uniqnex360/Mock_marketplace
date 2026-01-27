import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import MarketplaceCredential

# Get the test user
test_user = User.objects.get(username='testuser')

# Create Amazon AE credentials
amazon_cred = MarketplaceCredential.objects.create(
    user=test_user,
    marketplace='AMAZON_AE'
)
amazon_cred.generate_credentials()

print("✅ Amazon AE Credentials Created:")
print(f"   Client ID: {amazon_cred.client_id}")
print(f"   Client Secret: {amazon_cred.client_secret}")
print()

# Create Noon AE credentials
noon_cred = MarketplaceCredential.objects.create(
    user=test_user,
    marketplace='NOON_AE'
)
noon_cred.generate_credentials()

print("✅ Noon AE Credentials Created:")
print(f"   Client ID: {noon_cred.client_id}")
print(f"   Client Secret: {noon_cred.client_secret}")
print()

print("=" * 50)
print("📋 Summary - Save these credentials!")
print("=" * 50)
print(f"Username: testuser")
print(f"Password: testpass123")
print()
print(f"Amazon AE:")
print(f"  Client ID: {amazon_cred.client_id}")
print(f"  Client Secret: {amazon_cred.client_secret}")
print()
print(f"Noon AE:")
print(f"  Client ID: {noon_cred.client_id}")
print(f"  Client Secret: {noon_cred.client_secret}")