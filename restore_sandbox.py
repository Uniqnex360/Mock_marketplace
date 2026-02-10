import os
import django
import json

# --- DJANGO SETUP START ---
# This tells Python where your Django settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()
# --- DJANGO SETUP END ---

from django.contrib.auth.models import User
from apps.amazon_ae.models import *
from apps.noon_ae.models import *

def enrich_data():
    print("🏗️  Updating existing records with MongoDB JSON data...")
    
    # Path to your JSON folder
    json_path = 'mongodb_full_backup'

    def get_map(filename, key):
        file = os.path.join(json_path, f"{filename}.json")
        if not os.path.exists(file): 
            print(f"⚠️ Warning: {file} not found")
            return {}
        with open(file, 'r') as f:
            # We map by original ID for lookup
            return {str(item.get(key)): item for item in json.load(f)}

    # Load original data maps
    prod_map = get_map('product', 'product_id')
    prod_map.update(get_map('product', 'asin')) # Some use ASIN as key
    
    order_map = get_map('order', 'merchant_order_id')
    order_map.update(get_map('order', 'customer_order_id'))

    # 1. Update Amazon Products
    for p in AmazonProduct.objects.all():
        orig_id = p.asin.replace('999-', '')
        if orig_id in prod_map:
            p.raw_data = prod_map[orig_id]
            p.save()

    # 2. Update Amazon Orders
    for o in AmazonOrder.objects.all():
        orig_id = o.amazon_order_id.replace('999-', '')
        if orig_id in order_map:
            o.raw_data = order_map[orig_id]
            o.save()

    # 3. Update Noon Products
    for p in NoonProduct.objects.all():
        orig_id = p.noon_sku.replace('Z-', '').replace('-X', '')
        if orig_id in prod_map:
            p.raw_data = prod_map[orig_id]
            p.save()

    # 4. Update Noon Orders
    for o in NoonOrder.objects.all():
        orig_id = o.order_nr.replace('Z-', '')
        if orig_id in order_map:
            o.raw_data = order_map[orig_id]
            o.save()

    print("✅ Local database successfully enriched with all fields!")

if __name__ == "__main__":
    enrich_data()