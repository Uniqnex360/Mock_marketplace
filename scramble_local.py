import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem, AmazonProduct, AmazonInventory
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct, NoonInventory

@transaction.atomic
def transform_data_realistic():
    print("🔄 STARTING LOCAL ID TRANSFORMATION...")

    # ==========================================
    # 1. AMAZON DATA
    # ==========================================
    print("📦 Updating Amazon Data...")
    
    count = 0
    for order in AmazonOrder.objects.all():
        old_id = order.amazon_order_id
        if old_id.startswith("408-"):
            new_id = old_id.replace("408-", "999-", 1)
            order.amazon_order_id = new_id
            order.save()
            for item in order.items.all():
                if old_id in item.order_item_id:
                    item.order_item_id = item.order_item_id.replace(old_id, new_id)
                    item.save()
            count += 1
    print(f"   - Modified {count} Amazon Orders (408 -> 999)")

    count = 0
    for product in AmazonProduct.objects.all():
        old_sku = product.sku
        old_asin = product.asin
        if old_sku.endswith("-X"): continue

        new_sku = f"{old_sku}-X"
        new_asin = f"{old_asin}-X"

        AmazonInventory.objects.filter(sku=old_sku).update(sku=new_sku, asin=new_asin)
        AmazonOrderItem.objects.filter(sku=old_sku).update(sku=new_sku, asin=new_asin)
        
        product.sku = new_sku
        product.asin = new_asin
        product.save()
        count += 1
    print(f"   - Modified {count} Amazon Products")

    # ==========================================
    # 2. NOON DATA
    # ==========================================
    print("🌙 Updating Noon Data...")

    count = 0
    for order in NoonOrder.objects.all():
        old_id = order.order_nr
        if old_id.startswith("N-"):
            new_id = old_id.replace("N-", "Z-", 1)
            order.order_nr = new_id
            order.save()
            for item in order.items.all():
                if old_id in item.order_item_id:
                    item.order_item_id = item.order_item_id.replace(old_id, new_id)
                    item.save()
            count += 1
    print(f"   - Modified {count} Noon Orders (N -> Z)")

    count = 0
    for product in NoonProduct.objects.all():
        old_psku = product.partner_sku
        old_nsku = product.noon_sku
        if old_psku.endswith("-X"): continue

        new_psku = f"{old_psku}-X"
        new_nsku = f"{old_nsku}-X"

        NoonInventory.objects.filter(partner_sku=old_psku).update(partner_sku=new_psku, noon_sku=new_nsku)
        NoonOrderItem.objects.filter(partner_sku=old_psku).update(partner_sku=new_psku, noon_sku=new_nsku)
        
        product.partner_sku = new_psku
        product.noon_sku = new_nsku
        product.save()
        count += 1
    print(f"   - Modified {count} Noon Products")

    print("\n✅ LOCAL DATA TRANSFORMED SUCCESSFULLY!")

if __name__ == "__main__":
    transform_data_realistic()  