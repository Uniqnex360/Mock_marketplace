import os
import pandas as pd
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from apps.authentication.models import MarketplaceCredential
from apps.amazon_ae.models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct, NoonInventory

class Command(BaseCommand):
    help = 'Restore sandbox with dates forced to August 2025 and all fields populated'

    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️ Starting Sandbox Auto-Restore (Corrected August Dates)...")
        call_command('migrate', interactive=False)
        
        user, _ = User.objects.get_or_create(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Credentials Setup
        amz, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='AMAZON_AE')
        amz.client_id, amz.client_secret = "amazon_ae_yVkOidNBLFFQ0Lum0RhYSg", "ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
        amz.save()
        
        noon, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='NOON_AE')
        noon.client_id, noon.client_secret = "noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw", "Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"
        noon.save()

        if AmazonProduct.objects.count() == 0:
            self.stdout.write("📥 DB Empty. Restoring data...")
            path = os.path.join(settings.BASE_DIR, 'data_source')
            
            def get_df(name):
                return pd.read_excel(os.path.join(path, name)).where(pd.notnull, None)

            try:
                # 1. Amazon Products
                df_ap = get_df('amazon_products.xlsx')
                for _, r in df_ap.iterrows():
                    AmazonProduct.objects.update_or_create(asin=r['asin'], defaults={
                        'user': user, 'sku': r['sku'], 'title': r['title'], 'price': r['price'], 
                        'quantity': r['quantity'], 'status': 'ACTIVE',
                        # Map the missing fields if they exist in Excel
                        'product_title': r.get('product_title'),
                        'brand_name': r.get('brand_name'),
                        'listing_quality_score': r.get('listing_quality_score', 0),
                        'total_cogs': r.get('total_cogs', 0)
                    })

                # 2. Amazon Inventory
                df_ai = get_df('amazon_inventory.xlsx')
                for _, r in df_ai.iterrows():
                    AmazonInventory.objects.update_or_create(sku=r['sku'], user=user, defaults={
                        'asin': r['asin'], 'product_name': r['product_name'], 'available_quantity': r['available_quantity']
                    })

                # 3. Amazon Orders (FIXED DATE LOGIC)
                df_ao = get_df('amazon_orders.xlsx')
                for idx, r in df_ao.iterrows():
                    random_day = (idx % 28) + 1
                    hist_date = timezone.make_aware(datetime(2025, 8, random_day, 12, 0, 0))
                    
                    # We ONLY use hist_date here to ensure it is August 2025
                    AmazonOrder.objects.update_or_create(amazon_order_id=r['amazon_order_id'], defaults={
                        'user': user, 
                        'purchase_date': hist_date, 
                        'order_status': r['order_status'], 
                        'order_total_amount': r['order_total_amount'],
                        'buyer_email': r.get('buyer_email', ''),
                        'buyer_name': r.get('buyer_name', '')
                    })

                # 4. Noon Products
                df_np = get_df('noon_products.xlsx')
                for _, r in df_np.iterrows():
                    NoonProduct.objects.update_or_create(noon_sku=r['noon_sku'], defaults={
                        'user': user, 'partner_sku': r['partner_sku'], 'title': r['title'], 
                        'price': r['price'], 'stock_quantity': r['stock_quantity'], 'status': 'active',
                        'product_title': r.get('product_title'),
                        'brand_name': r.get('brand_name')
                    })

                # 5. Noon Inventory
                df_ni = get_df('noon_inventory.xlsx')
                for _, r in df_ni.iterrows():
                    NoonInventory.objects.update_or_create(partner_sku=r['partner_sku'], user=user, defaults={
                        'noon_sku': r['noon_sku'], 'barcode': r['barcode'], 'quantity': r['quantity']
                    })

                # 6. Noon Orders (FIXED DATE LOGIC)
                df_no = get_df('noon_orders.xlsx')
                for idx, r in df_no.iterrows():
                    random_day = (idx % 28) + 1
                    hist_date = timezone.make_aware(datetime(2025, 8, random_day, 15, 30, 0))
                    
                    NoonOrder.objects.update_or_create(order_nr=r['order_nr'], defaults={
                        'user': user, 
                        'order_date': hist_date, 
                        'status': r['status'], 
                        'total_amount': r['total_amount'],
                        'customer_first_name': r.get('customer_first_name', ''),
                        'customer_last_name': r.get('customer_last_name', '')
                    })

                self.stdout.write(self.style.SUCCESS("✅ SUCCESS: All data restored with August 2025 dates!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Restore failed: {str(e)}"))