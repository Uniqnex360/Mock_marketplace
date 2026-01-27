from django.contrib import admin
from .models import MarketplaceCredential

@admin.register(MarketplaceCredential)
class MarketplaceCredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'marketplace', 'client_id', 'is_active', 'created_at']
    list_filter = ['marketplace', 'is_active']
    search_fields = ['user__username', 'client_id']