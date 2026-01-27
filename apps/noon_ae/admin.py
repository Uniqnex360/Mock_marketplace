from django.contrib import admin
from .models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory

@admin.register(NoonProduct)
class NoonProductAdmin(admin.ModelAdmin):
    list_display = ['noon_sku', 'partner_sku', 'title', 'price', 'stock_quantity', 'status']
    search_fields = ['noon_sku', 'partner_sku', 'title']
    list_filter = ['status', 'created_at']

@admin.register(NoonOrder)
class NoonOrderAdmin(admin.ModelAdmin):
    list_display = ['order_nr', 'order_date', 'status', 'total_amount']
    search_fields = ['order_nr', 'customer_email']
    list_filter = ['status', 'order_date']

@admin.register(NoonOrderItem)
class NoonOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_item_id', 'noon_sku', 'name', 'quantity']
    search_fields = ['order_item_id', 'noon_sku', 'name']

@admin.register(NoonInventory)
class NoonInventoryAdmin(admin.ModelAdmin):
    list_display = ['partner_sku', 'noon_sku', 'quantity', 'reserved_quantity']
    search_fields = ['partner_sku', 'noon_sku']