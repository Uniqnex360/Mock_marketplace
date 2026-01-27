from django.db import models
from django.contrib.auth.models import User
import secrets
from datetime import datetime, timedelta

class MarketplaceCredential(models.Model):
    MARKETPLACE_CHOICES = [
        ('AMAZON_AE', 'Amazon AE'),
        ('NOON_AE', 'Noon AE'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    marketplace = models.CharField(max_length=20, choices=MARKETPLACE_CHOICES)
    client_id = models.CharField(max_length=100, unique=True)
    client_secret = models.CharField(max_length=200)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'marketplace']

    def generate_credentials(self):
        self.client_id = f"{self.marketplace.lower()}_{secrets.token_urlsafe(16)}"
        self.client_secret = secrets.token_urlsafe(32)
        self.save()

    def generate_access_token(self):
        self.access_token = secrets.token_urlsafe(64)
        self.token_expires_at = datetime.now() + timedelta(hours=24)
        self.save()
        return self.access_token

    def verify_secret(self, secret):
        return self.client_secret == secret