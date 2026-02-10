import os
import django
import pymongo
from pymongo import MongoClient
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from apps.noon_ae.models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory
from django.contrib.auth.models import User

MONGODB_URI = 'mongodb+srv://techteam:WcblsEme1Q1Vv7Rt@cluster0.5hrxigl.mongodb.net/ecommerce_db?retryWrites=true&w=majority&appName=Cluster0'

DEFAULT_USER = None

def get_default_user():
    global DEFAULT_USER
    if DEFAULT_USER is None:
        DEFAULT_USER, _ = User.objects.get_or_create(username='admin')
    return DEFAULT_USER

def connect_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client['ecommerce_db']
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def find_products_by_sku(db, sku_list):
    """Find products in MongoDB by SKU"""
    if not db:
        return []
    
    product_collection = db['product']
    products = list(product_collection.find({'sku': {'$in': sku_list}}))
    return products

def find_products_by_asin(db, asin_list):
    """Find products in MongoDB by ASIN/product_id"""
    if not db:
        return []
    
    product_collection = db['product']
    products = list(product_collection.find({'product_id': {'$in': asin_list}}))
    return products

def import_amazon_products():
    """Import Amazon products that are referenced in existing orders"""
    print("\n🔍 Scanning Amazon orders for missing products...")
    
    db = connect_mongodb()
    user = get_default_user()
    
    # Get all unique SKUs and ASINs from order items
    order_items = AmazonOrderItem.objects.all()
    skus = set()
    asins = set()
    
    for item in order_items:
        if item.sku:
            skus.add(item.sku)
        if item.asin:
            asins.add(item.asin)
    
    print(f"   Found {len(skus)} unique SKUs and {len(asins)} unique ASINs in orders")
    
    # Check which SKUs/ASINs already have product records
    existing_products = AmazonProduct.objects.all()
    existing_skus = set(p.sku for p in existing_products)
    existing_asins = set(p.asin for p in existing_products)
    
    missing_skus = skus - existing_skus
    missing_asins = asins - existing_asins
    
    print(f"   Missing {len(missing_skus)} SKUs and {len(missing_asins)} ASINs")
    
    if not missing_skus and not missing_asins:
        print("   ✅ All products already exist!")
        return
    
    # Find products in MongoDB
    mongodb_products = []
    
    if missing_skus and db:
        try:
            skus_list = list(missing_skus)[:100]  # Limit to 100 for query
            products = find_products_by_sku(db, skus_list)
            mongodb_products.extend(products)
            print(f"   ✅ Found {len(products)} products by SKU in MongoDB")
        except Exception as e:
            print(f"   ⚠️  Error finding products by SKU: {e}")
    
    if missing_asins and db:
        try:
            asins_list = list(missing_asins)[:100]  # Limit to 100 for query
            products = find_products_by_asin(db, asins_list)
            
            # Filter out duplicates
            existing_ids = {p.get('_id') for p in mongodb_products}
            products = [p for p in products if p.get('_id') not in existing_ids]
            
            mongodb_products.extend(products)
            print(f"   ✅ Found {len(products)} products by ASIN in MongoDB")
        except Exception as e:
            print(f"   ⚠️  Error finding products by ASIN: {e}")
    
    # Import found products
    usd_to_aed = 3.67
    imported_count = 0
    
    for product in mongodb_products:
        try:
            # Check if product already exists
            sku = product.get('sku', f"SKU-{random.randint(1000, 9999)}")
            asin = product.get('product_id', f"B{random.randint(100000000, 999999999)}")
            
            if AmazonProduct.objects.filter(sku=sku, asin=asin).exists():
                continue
            
            # Convert price to AED
            price = float(product.get('price', 0))
            if product.get('currency', '$') == '$':
                price = price * usd_to_aed
            
            # Get image URL
            image_url = product.get('image_url', '')
            if not image_url and product.get('image_urls'):
                image_url = product['image_urls'][0] if product['image_urls'] else ''
            
            # Create product
            amazon_product = AmazonProduct(
                user=user,
                asin=asin,
                sku=sku,
                title=product.get('product_title', 'Unknown Product')[:500],
                description=product.get('product_description', '')[:2000],
                brand=product.get('brand_name', 'Generic')[:200],
                category=product.get('category', 'General')[:200],
                price=round(price, 2),
                currency='AED',
                quantity=int(product.get('quantity', 0)),
                image_url=image_url,
                status='ACTIVE'
            )
            amazon_product.save()
            imported_count += 1
            
        except Exception as e:
            print(f"   ⚠️  Error importing product: {e}")
    
    print(f"   ✅ Imported {imported_count} Amazon products")

def import_noon_products():
    """Import Noon products that are referenced in existing orders"""
    print("\n🔍 Scanning Noon orders for missing products...")
    
    db = connect_mongodb()
    user = get_default_user()
    
    # Get all unique SKUs from order items
    order_items = NoonOrderItem.objects.all()
    partner_skus = set()
    noon_skus = set()
    
    for item in order_items:
        if item.partner_sku:
            partner_skus.add(item.partner_sku)
        if item.noon_sku:
            noon_skus.add(item.noon_sku)
    
    print(f"   Found {len(partner_skus)} unique partner SKUs and {len(noon_skus)} unique Noon SKUs in orders")
    
    # Check which SKUs already have product records
    existing_products = NoonProduct.objects.all()
    existing_partner_skus = set(p.partner_sku for p in existing_products)
    existing_noon_skus = set(p.noon_sku for p in existing_products)
    
    missing_partner_skus = partner_skus - existing_partner_skus
    missing_noon_skus = noon_skus - existing_noon_skus
    
    print(f"   Missing {len(missing_partner_skus)} partner SKUs and {len(missing_noon_skus)} Noon SKUs")
    
    if not missing_partner_skus and not missing_noon_skus:
        print("   ✅ All products already exist!")
        return
    
    # Find products in MongoDB
    mongodb_products = []
    
    if missing_partner_skus and db:
        try:
            skus_list = list(missing_partner_skus)[:100]  # Limit to 100 for query
            products = find_products_by_sku(db, skus_list)
            mongodb_products.extend(products)
            print(f"   ✅ Found {len(products)} products by SKU in MongoDB")
        except Exception as e:
            print(f"   ⚠️  Error finding products by SKU: {e}")
    
    # Import found products
    usd_to_aed = 3.67
    imported_count = 0
    
    for product in mongodb_products:
        try:
            # Check if product already exists
            partner_sku = product.get('sku', f"PART-{random.randint(1000, 9999)}")
            noon_sku = f"N-{partner_sku}"
            
            if NoonProduct.objects.filter(partner_sku=partner_sku).exists():
                continue
            
            # Convert price to AED
            price = float(product.get('price', 0))
            if product.get('currency', '$') == '$':
                price = price * usd_to_aed
            
            # Get image URL
            image_url = product.get('image_url', '')
            if not image_url and product.get('image_urls'):
                image_url = product['image_urls'][0] if product['image_urls'] else ''
            
            # Create product
            noon_product = NoonProduct(
                user=user,
                noon_sku=noon_sku,
                partner_sku=partner_sku,
                title=product.get('product_title', 'Unknown Product')[:500],
                title_ar=f"منتج {partner_sku}",
                summary=product.get('product_description', '')[:500],
                brand=product.get('brand_name', 'Generic')[:200],
                category_code=product.get('category', 'general')[:100],
                product_type=product.get('product_type', 'General')[:100],
                price=round(price, 2),
                stock_quantity=int(product.get('quantity', 0)),
                status='active',
                image_url=image_url
            )
            noon_product.save()
            imported_count += 1
            
        except Exception as e:
            print(f"   ⚠️  Error importing product: {e}")
    
    print(f"   ✅ Imported {imported_count} Noon products")

def main():
    print("🚀 Starting product import from MongoDB based on existing orders...")
    
    import_amazon_products()
    import_noon_products()
    
    print("\n✅ Product import complete!")
    
    # Show summary
    print(f"\n📊 Database Summary:")
    print(f"   Amazon Products: {AmazonProduct.objects.count()}")
    print(f"   Amazon Orders: {AmazonOrder.objects.count()}")
    print(f"   Amazon Order Items: {AmazonOrderItem.objects.count()}")
    print(f"   Noon Products: {NoonProduct.objects.count()}")
    print(f"   Noon Orders: {NoonOrder.objects.count()}")
    print(f"   Noon Order Items: {NoonOrderItem.objects.count()}")

if __name__ == '__main__':
    main()
