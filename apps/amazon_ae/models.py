from django.db import models
from django.contrib.auth.models import User

class AmazonProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amazon_products')
    asin = models.CharField(max_length=50, default='')
    sku = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='') 
    brand = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AED')
    quantity = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=50, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asin} - {self.title}"

class AmazonOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Unshipped', 'Unshipped'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amazon_orders')
    amazon_order_id = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateTimeField()
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    fulfillment_channel = models.CharField(max_length=10, default='MFN')
    sales_channel = models.CharField(max_length=50, default='Amazon.ae')
    order_total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_total_currency = models.CharField(max_length=3, default='AED')
    number_of_items_shipped = models.IntegerField(default=0)
    number_of_items_unshipped = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50, default='Other')
    marketplace_id = models.CharField(max_length=50, default='A2VIGQ35RCS4UG')
    buyer_email = models.EmailField(blank=True)
    buyer_name = models.CharField(max_length=200, blank=True)
    ship_service_level = models.CharField(max_length=100, blank=True)
    earliest_ship_date = models.DateTimeField(null=True, blank=True)
    latest_ship_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.amazon_order_id

class AmazonOrderItem(models.Model):
    order = models.ForeignKey(AmazonOrder, on_delete=models.CASCADE, related_name='items')
    order_item_id = models.CharField(max_length=50, unique=True)
    asin = models.CharField(max_length=50)
    sku = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    quantity_ordered = models.IntegerField()
    quantity_shipped = models.IntegerField(default=0)
    item_price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    item_price_currency = models.CharField(max_length=3, default='AED')
    shipping_price_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    item_tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promotion_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    condition_id = models.CharField(max_length=50, default='New')
    is_gift = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.order_item_id} - {self.title}"

class AmazonInventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amazon_inventory')
    asin = models.CharField(max_length=50)
    sku = models.CharField(max_length=100)
    fn_sku = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(max_length=500)
    condition = models.CharField(max_length=50, default='new')
    available_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    total_quantity = models.IntegerField(default=0)
    warehouse_condition_code = models.CharField(max_length=50, blank=True)
    last_updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'sku']

    def __str__(self):
        return f"{self.sku} - {self.available_quantity}"