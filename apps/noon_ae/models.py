from django.db import models
from django.contrib.auth.models import User

class NoonProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noon_products')
    noon_sku = models.CharField(max_length=100, unique=True)
    partner_sku = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    title_ar = models.CharField(max_length=500, blank=True)
    summary = models.TextField(blank=True)
    brand = models.CharField(max_length=200)
    category_code = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)
    warranty = models.CharField(max_length=100, blank=True)
    stock_quantity = models.IntegerField(default=0)
    max_order_quantity = models.IntegerField(default=10)
    status = models.CharField(max_length=50, default='active')
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.noon_sku} - {self.title}"

class NoonOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noon_orders')
    order_nr = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AED')
    delivery_provider = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100)
    address_area = models.CharField(max_length=200, blank=True)
    address_street = models.CharField(max_length=200, blank=True)
    is_express = models.BooleanField(default=False)
    is_marketplace = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return self.order_nr

class NoonOrderItem(models.Model):
    order = models.ForeignKey(NoonOrder, on_delete=models.CASCADE, related_name='items')
    order_item_id = models.CharField(max_length=50, unique=True)
    noon_sku = models.CharField(max_length=100)
    partner_sku = models.CharField(max_length=100)
    raw_data = models.JSONField(default=dict)
    name = models.CharField(max_length=500)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50)
    delivery_date = models.DateTimeField(null=True, blank=True)
    return_eligible_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_item_id} - {self.name}"

class NoonInventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noon_inventory')
    noon_sku = models.CharField(max_length=100)
    partner_sku = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50, blank=True)
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    warehouse_code = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'partner_sku']

    def __str__(self):
        return f"{self.partner_sku} - {self.quantity}"