import random
from django.core.management import setup_environ
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem, AmazonProduct
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct

def fix_amazon_order_items():
    """Link order items with actual products"""
    
    # Get all products
    products = list(AmazonProduct.objects.all())
    if not products:
        print("No products found!")
        return
    
    print(f"Found {len(products)} Amazon products")
    
    # Fix each order item
    order_items = AmazonOrderItem.objects.all()
    updated = 0
    
    for item in order_items:
        # If item has generic data, link it to a real product
        if item.title == "Product" or item.sku.startswith("SKU-"):
            # Pick a random product
            product = random.choice(products)
            
            # Update item with real product data
            item.asin = product.asin
            item.sku = product.sku
            item.title = product.title
            
            # Set realistic quantity
            item.quantity_ordered = random.randint(1, 3)
            
            # Set price based on product
            item.item_price_amount = product.price * item.quantity_ordered
            
            item.save()
            updated += 1
    
    print(f"✅ Updated {updated} Amazon order items with real product data")
    
    # Update order totals
    for order in AmazonOrder.objects.all():
        total = sum(item.item_price_amount for item in order.items.all())
        if total > 0:
            order.order_total_amount = total
            order.save()
    
    print("✅ Updated order totals")

def fix_noon_order_items():
    """Link Noon order items with actual products"""
    
    # Get all Noon products
    products = list(NoonProduct.objects.all())
    if not products:
        print("No Noon products found!")
        return
    
    print(f"Found {len(products)} Noon products")
    
    # Fix each order item
    order_items = NoonOrderItem.objects.all()
    updated = 0
    
    for item in order_items:
        # If item has generic data, link it to a real product
        if "HYD-" not in item.partner_sku and "RB-" not in item.partner_sku:
            # Pick a random product
            product = random.choice(products)
            
            # Update item with real product data
            item.noon_sku = product.noon_sku
            item.partner_sku = product.partner_sku
            item.name = product.title
            
            # Set realistic quantity
            if item.quantity == 0:
                item.quantity = random.randint(1, 3)
            
            # Set price based on product
            item.unit_price = product.price
            item.total_price = product.price * item.quantity
            
            item.save()
            updated += 1
    
    print(f"✅ Updated {updated} Noon order items with real product data")
    
    # Update order totals
    for order in NoonOrder.objects.all():
        total = sum(item.total_price for item in order.items.all())
        if total > 0:
            order.total_amount = total
            order.save()
    
    print("✅ Updated Noon order totals")

def create_missing_order_items():
    """Create order items for orders that don't have any"""
    
    # Amazon orders without items
    amazon_orders_without_items = AmazonOrder.objects.filter(items__isnull=True)
    products = list(AmazonProduct.objects.all()[:100])  # Use first 100 products
    
    if amazon_orders_without_items.exists() and products:
        print(f"Creating items for {amazon_orders_without_items.count()} Amazon orders without items...")
        
        for order in amazon_orders_without_items:
            # Create 1-3 items per order
            num_items = random.randint(1, 3)
            order_total = 0
            
            for i in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                
                AmazonOrderItem.objects.create(
                    order=order,
                    order_item_id=f"{order.amazon_order_id}-ITEM-{i+1}",
                    asin=product.asin,
                    sku=product.sku,
                    title=product.title,
                    quantity_ordered=quantity,
                    quantity_shipped=quantity if order.order_status in ['Delivered', 'Shipped'] else 0,
                    item_price_amount=product.price,
                    item_price_currency='AED'
                )
                
                order_total += product.price * quantity
            
            # Update order total
            order.order_total_amount = order_total
            order.save()
        
        print(f"✅ Created items for {amazon_orders_without_items.count()} Amazon orders")
    
    # Noon orders without items
    noon_orders_without_items = NoonOrder.objects.filter(items__isnull=True)
    noon_products = list(NoonProduct.objects.all()[:100])
    
    if noon_orders_without_items.exists() and noon_products:
        print(f"Creating items for {noon_orders_without_items.count()} Noon orders without items...")
        
        for order in noon_orders_without_items:
            # Create 1-3 items per order
            num_items = random.randint(1, 3)
            order_total = 0
            
            for i in range(num_items):
                product = random.choice(noon_products)
                quantity = random.randint(1, 3)
                
                NoonOrderItem.objects.create(
                    order=order,
                    order_item_id=f"{order.order_nr}-ITEM-{i+1}",
                    noon_sku=product.noon_sku,
                    partner_sku=product.partner_sku,
                    name=product.title,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity,
                    status=order.status
                )
                
                order_total += product.price * quantity
            
            # Update order total
            order.total_amount = order_total
            order.save()
        
        print(f"✅ Created items for {noon_orders_without_items.count()} Noon orders")

if __name__ == "__main__":
    print("🔧 Fixing order items...")
    
    # Fix existing items
    fix_amazon_order_items()
    fix_noon_order_items()
    
    # Create missing items
    create_missing_order_items()
    
    print("\n✅ All order items fixed!")
    
    # Show summary
    from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem
    from apps.noon_ae.models import NoonOrder, NoonOrderItem
    
    amazon_orders = AmazonOrder.objects.count()
    amazon_items = AmazonOrderItem.objects.count()
    noon_orders = NoonOrder.objects.count()
    noon_items = NoonOrderItem.objects.count()
    
    print(f"\n📊 Summary:")
    print(f"Amazon: {amazon_orders} orders with {amazon_items} items")
    print(f"Noon: {noon_orders} orders with {noon_items} items")