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
    product_title = models.CharField(max_length=500, null=True, blank=True)
    listing_quality_score = models.FloatField(null=True, blank=True)
    total_cogs = models.FloatField(null=True, blank=True)
    product_cost = models.FloatField(null=True, blank=True)
    referral_fee = models.FloatField(null=True, blank=True)
    wpid = models.CharField(max_length=100, null=True, blank=True)
    brand_name = models.CharField(max_length=200, null=True, blank=True)
    attributes = models.JSONField(default=dict, blank=True) # For complex MongoDB objects
    features = models.JSONField(default=list, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    image_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=50, default='ACTIVE')
    raw_data = models.JSONField(default=dict) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cogs = models.FloatField(default=0.0, null=True, blank=True)
    shipping_cost = models.FloatField(default=0.0, null=True, blank=True)
    a_shipping_cost = models.FloatField(default=0.0, null=True, blank=True)
    channel_fee = models.FloatField(default=0.0, null=True, blank=True)
    fullfillment_by_channel_fee = models.FloatField(default=0.0, null=True, blank=True)
    
    # Metrics
    page_views = models.IntegerField(default=0, null=True, blank=True)
    sessions = models.IntegerField(default=0, null=True, blank=True)
    refund = models.IntegerField(default=0, null=True, blank=True)
    
    # Descriptions & Meta
    product_description = models.TextField(null=True, blank=True)
    product_id = models.CharField(max_length=100, null=True, blank=True)
    product_type = models.CharField(max_length=100, null=True, blank=True)
    manufacturer_name = models.CharField(max_length=200, null=True, blank=True)
    pack_size = models.IntegerField(default=1, null=True, blank=True)
    
    # Flags
    fullfillment_by_channel = models.BooleanField(default=False)
    will_ship_internationally = models.BooleanField(default=False)
    new_product = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    
    # Complex Types
    variant_group_info = models.JSONField(default=dict, blank=True)
    marketplace_ids = models.JSONField(default=list, blank=True)

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
    order_total = models.JSONField(default=dict, blank=True)
    shipping_information = models.JSONField(default=dict, blank=True)
    is_prime = models.BooleanField(default=False)
    geo = models.CharField(max_length=50, null=True, blank=True)
    customer_order_id = models.CharField(max_length=100, null=True, blank=True)
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
    raw_data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    merchant_order_id = models.CharField(max_length=100, null=True, blank=True)
    automated_shipping_settings = models.JSONField(default=dict, blank=True)
    is_business_order = models.BooleanField(default=False)
    is_prime = models.BooleanField(default=False)
    
    purchase_order_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.amazon_order_id

class AmazonOrderItem(models.Model):
    order = models.ForeignKey(AmazonOrder, on_delete=models.CASCADE, related_name='items')
    order_item_id = models.CharField(max_length=50, unique=True)
    asin = models.CharField(max_length=50)
    sku = models.CharField(max_length=100)
    raw_data = models.JSONField(default=dict)
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
    Pricing = models.JSONField(default=dict, blank=True)
    TaxCollection = models.JSONField(default=dict, blank=True)
    ProductDetails = models.JSONField(default=dict, blank=True)
    PromotionDiscount = models.JSONField(default=dict, blank=True)
    Fulfillment = models.JSONField(default=dict, blank=True)
    
    # Financials
    net_profit = models.FloatField(null=True, blank=True)
    Platform = models.CharField(max_length=100, null=True, blank=True)

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