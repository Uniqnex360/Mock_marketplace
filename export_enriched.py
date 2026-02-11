import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonProduct, AmazonOrder, AmazonOrderItem
from apps.noon_ae.models import NoonProduct, NoonOrder, NoonOrderItem

def export():
    print("📤 Exporting fully enriched subset to JSON...")
    
    data = {
        # Export all products with all fields
        "amazon_products": list(AmazonProduct.objects.all().values()),
        "amazon_orders": [],
        "noon_products": list(NoonProduct.objects.all().values()),
        "noon_orders": []
    }

    # Export Amazon Orders + Items
    for o in AmazonOrder.objects.all():
        order_dict = {
            "amazon_order_id": o.amazon_order_id,
            "order_status": o.order_status,
            "order_total": o.order_total,
            "shipping_information": o.shipping_information,
            "geo": o.geo,
            "items": list(o.items.all().values())
        }
        data["amazon_orders"].append(order_dict)

    # Export Noon Orders + Items
    for o in NoonOrder.objects.all():
        order_dict = {
            "order_nr": o.order_nr,
            "status": o.status,
            "order_total": o.order_total,
            "shipping_information": o.shipping_information,
            "geo": o.geo,
            "items": list(o.items.all().values())
        }
        data["noon_orders"].append(order_dict)

    # Ensure the data_source directory exists
    os.makedirs('data_source', exist_ok=True)

    with open('data_source/enriched_subset.json', 'w') as f:
        # Use default=str to handle datetime objects
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Created data_source/enriched_subset.json")
    print(f"📁 Size: {os.path.getsize('data_source/enriched_subset.json') / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    export()