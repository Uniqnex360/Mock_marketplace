import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem, AmazonProduct
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct

def fix_amazon_order_items():
    """Match order items to real products by SKU or assign random products"""
    
    products = list(AmazonProduct.objects.all())
    if not products:
        print("No products found!")
        return
    
    print(f"Found {len(products)} Amazon products")
    
    # Create SKU to product mapping
    sku_to_product = {}
    for product in products:
        sku_to_product[product.sku] = product
    
    order_items = AmazonOrderItem.objects.all()
    updated_by_sku = 0
    updated_random = 0
    
    for item in order_items:
        # Try to match by SKU first
        if item.sku in sku_to_product:
            product = sku_to_product[item.sku]
            item.asin = product.asin
            item.title = product.title
            # Update price based on product
            item.item_price_amount = product.price
            item.save()
            updated_by_sku += 1
        else:
            # Assign a random product
            product = random.choice(products)
            item.asin = product.asin
            item.sku = product.sku
            item.title = product.title
            
            # Keep existing quantity or set realistic one
            if item.quantity_ordered == 0:
                item.quantity_ordered = random.randint(1, 3)
            
            # Set price based on product
            item.item_price_amount = product.price
            item.save()
            updated_random += 1
    
    print(f"✅ Updated {updated_by_sku} items by matching SKU")
    print(f"✅ Updated {updated_random} items with random products")
    
    # Update order totals based on actual items
    for order in AmazonOrder.objects.all():
        total = 0
        items_count = 0
        for item in order.items.all():
            total += item.item_price_amount * item.quantity_ordered
            items_count += item.quantity_ordered
        
        order.order_total_amount = total
        order.number_of_items_unshipped = items_count if order.order_status in ['Pending', 'Processing'] else 0
        order.number_of_items_shipped = items_count if order.order_status in ['Shipped', 'Delivered'] else 0
        order.save()
    
    print("✅ Updated Amazon order totals")

def fix_noon_order_items():
    """Match Noon order items to real products"""
    
    products = list(NoonProduct.objects.all())
    if not products:
        print("No Noon products found!")
        return
    
    print(f"Found {len(products)} Noon products")
    
    # Create SKU to product mapping
    sku_to_product = {}
    for product in products:
        sku_to_product[product.partner_sku] = product
    
    order_items = NoonOrderItem.objects.all()
    updated_by_sku = 0
    updated_random = 0
    
    for item in order_items:
        # Try to match by partner SKU first
        if item.partner_sku in sku_to_product:
            product = sku_to_product[item.partner_sku]
            item.noon_sku = product.noon_sku
            item.name = product.title
            # Update price based on product
            item.unit_price = product.price
            item.total_price = product.price * item.quantity
            item.save()
            updated_by_sku += 1
        else:
            # Assign a random product for items without matches
            product = random.choice(products)
            item.noon_sku = product.noon_sku
            item.partner_sku = product.partner_sku
            item.name = product.title
            
            # Keep existing quantity or set realistic one
            if item.quantity == 0:
                item.quantity = random.randint(1, 3)
            
            # Set price based on product
            item.unit_price = product.price
            item.total_price = product.price * item.quantity
            item.save()
            updated_random += 1
    
    print(f"✅ Updated {updated_by_sku} Noon items by matching SKU")
    print(f"✅ Updated {updated_random} Noon items with random products")
    
    # Update order totals
    for order in NoonOrder.objects.all():
        total = sum(item.total_price for item in order.items.all())
        if total > 0:
            order.total_amount = total
            order.save()
    
    print("✅ Updated Noon order totals")

def verify_data():
    """Verify the fixes worked"""
    print("\n📊 Verification:")
    
    # Check Amazon
    order_asins = set(AmazonOrderItem.objects.values_list('asin', flat=True))
    product_asins = set(AmazonProduct.objects.values_list('asin', flat=True))
    matching_asins = order_asins & product_asins
    
    print(f"Amazon order ASINs matching products: {len(matching_asins)}/{len(order_asins)}")
    
    # Show sample items
    print("\nSample Amazon order items after fix:")
    for item in AmazonOrderItem.objects.all()[:3]:
        print(f"  - {item.asin}: {item.title[:50]}... (${item.item_price_amount})")
    
    # Check Noon
    noon_order_skus = set(NoonOrderItem.objects.values_list('partner_sku', flat=True))
    noon_product_skus = set(NoonProduct.objects.values_list('partner_sku', flat=True))
    matching_skus = noon_order_skus & noon_product_skus
    
    print(f"\nNoon order SKUs matching products: {len(matching_skus)}/{len(noon_order_skus)}")
    
    # Show sample items
    print("\nSample Noon order items after fix:")
    for item in NoonOrderItem.objects.all()[:3]:
        print(f"  - {item.partner_sku}: {item.name[:50]}... (AED {item.unit_price})")

if __name__ == "__main__":
    print("🔧 Fixing order items to use real products...")
    
    fix_amazon_order_items()
    print()
    fix_noon_order_items()
    
    verify_data()
    
    print("\n✅ All order items now linked to real products!")