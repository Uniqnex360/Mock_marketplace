import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem, AmazonProduct, AmazonInventory
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct, NoonInventory

OUTPUT_DIR = "render_upload_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def remove_tz(data_list):
    """Helper to remove timezones from dictionaries"""
    cleaned_list = []
    for item in data_list:
        new_item = {}
        for k, v in item.items():
            if isinstance(v, datetime) and v.tzinfo:
                new_item[k] = v.replace(tzinfo=None)
            else:
                new_item[k] = v
        cleaned_list.append(new_item)
    return cleaned_list

def export_data():
    print("📤 Exporting modified data to Excel...")

    # 1. Amazon Products
    products = list(AmazonProduct.objects.all().values())
    products = remove_tz(products)  # Clean timezones
    pd.DataFrame(products).to_excel(f"{OUTPUT_DIR}/amazon_products.xlsx", index=False)
    print("   - Amazon Products exported")

    # 2. Amazon Orders (Flattened)
    orders_data = []
    for order in AmazonOrder.objects.all():
        items = order.items.all()
        base_order = {
            'amazon_order_id': order.amazon_order_id,
            'purchase_date': order.purchase_date.replace(tzinfo=None) if order.purchase_date else None,
            'order_status': order.order_status,
            'order_total_amount': order.order_total_amount,
            'buyer_email': order.buyer_email,
            'buyer_name': order.buyer_name
        }
        
        if not items:
            orders_data.append(base_order)
        else:
            for item in items:
                row = base_order.copy()
                row.update({
                    'order_item_id': item.order_item_id,
                    'item_asin': item.asin,
                    'item_sku': item.sku,
                    'item_title': item.title,
                    'quantity_ordered': item.quantity_ordered,
                    'item_price': item.item_price_amount
                })
                orders_data.append(row)
    
    pd.DataFrame(orders_data).to_excel(f"{OUTPUT_DIR}/amazon_orders.xlsx", index=False)
    print("   - Amazon Orders exported")

    # 3. Amazon Inventory
    inv = list(AmazonInventory.objects.all().values())
    inv = remove_tz(inv)
    pd.DataFrame(inv).to_excel(f"{OUTPUT_DIR}/amazon_inventory.xlsx", index=False)
    print("   - Amazon Inventory exported")

    # 4. Noon Products
    n_products = list(NoonProduct.objects.all().values())
    n_products = remove_tz(n_products)
    pd.DataFrame(n_products).to_excel(f"{OUTPUT_DIR}/noon_products.xlsx", index=False)
    print("   - Noon Products exported")

    # 5. Noon Orders
    n_orders_data = []
    for order in NoonOrder.objects.all():
        items = order.items.all()
        base_order = {
            'order_nr': order.order_nr,
            'order_date': order.order_date.replace(tzinfo=None) if order.order_date else None,
            'status': order.status,
            'customer_first_name': order.customer_first_name,
            'customer_last_name': order.customer_last_name,
            'customer_email': order.customer_email,
            'total_amount': order.total_amount,
            'address_city': order.address_city
        }

        if not items:
            n_orders_data.append(base_order)
        else:
            for item in items:
                row = base_order.copy()
                row.update({
                    'order_item_id': item.order_item_id,
                    'item_noon_sku': item.noon_sku,
                    'item_partner_sku': item.partner_sku,
                    'item_name': item.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                    'item_status': item.status
                })
                n_orders_data.append(row)
    
    pd.DataFrame(n_orders_data).to_excel(f"{OUTPUT_DIR}/noon_orders.xlsx", index=False)
    print("   - Noon Orders exported")

    # 6. Noon Inventory
    n_inv = list(NoonInventory.objects.all().values())
    n_inv = remove_tz(n_inv)
    pd.DataFrame(n_inv).to_excel(f"{OUTPUT_DIR}/noon_inventory.xlsx", index=False)
    print("   - Noon Inventory exported")

    print("\n✅ All files ready in 'render_upload_files/' directory!")

if __name__ == "__main__":
    export_data()