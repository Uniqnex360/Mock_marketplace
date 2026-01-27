from django.contrib import admin
from .models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory

@admin.register(AmazonProduct)
class AmazonProductAdmin(admin.ModelAdmin):
    list_display = ['asin', 'sku', 'title', 'price', 'quantity', 'status']
    search_fields = ['asin', 'sku', 'title']
    list_filter = ['status', 'created_at']

@admin.register(AmazonOrder)
class AmazonOrderAdmin(admin.ModelAdmin):
    list_display = ['amazon_order_id', 'purchase_date', 'order_status', 'order_total_amount']
    search_fields = ['amazon_order_id', 'buyer_email']
    list_filter = ['order_status', 'purchase_date']

@admin.register(AmazonOrderItem)
class AmazonOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_item_id', 'asin', 'title', 'quantity_ordered']
    search_fields = ['order_item_id', 'asin', 'title']

@admin.register(AmazonInventory)
class AmazonInventoryAdmin(admin.ModelAdmin):
    list_display = ['sku', 'asin', 'available_quantity', 'total_quantity']
    search_fields = ['sku', 'asin']