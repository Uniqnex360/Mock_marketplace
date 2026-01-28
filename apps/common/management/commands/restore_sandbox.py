import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from apps.authentication.models import MarketplaceCredential
from apps.amazon_ae.models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct, NoonInventory

class Command(BaseCommand):
    help = 'Complete sandbox restoration including Inventory'

    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️ Starting Full Sandbox Auto-Restore...")
        call_command('migrate', interactive=False)
        
        user, _ = User.objects.get_or_create(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Setup Credentials
        amz, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='AMAZON_AE')
        amz.client_id, amz.client_secret = "amazon_ae_yVkOidNBLFFQ0Lum0RhYSg", "ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
        amz.save()
        
        noon, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='NOON_AE')
        noon.client_id, noon.client_secret = "noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw", "Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"
        noon.save()

        if AmazonProduct.objects.count() == 0:
            self.stdout.write("📥 DB is empty. Importing everything...")
            path = os.path.join(settings.BASE_DIR, 'data_source')
            
            def get_df(name):
                return pd.read_excel(os.path.join(path, name)).where(pd.notnull, None)

            try:
                # 1. Amazon Products
                df_ap = get_df('amazon_products.xlsx')
                for _, r in df_ap.iterrows():
                    AmazonProduct.objects.update_or_create(asin=r['asin'], defaults={
                        'user': user, 'sku': r['sku'], 'title': r['title'], 'price': r['price'], 'quantity': r['quantity'], 'status': 'ACTIVE'
                    })

                # 2. Amazon Inventory (NEW)
                df_ai = get_df('amazon_inventory.xlsx')
                for _, r in df_ai.iterrows():
                    AmazonInventory.objects.update_or_create(sku=r['sku'], user=user, defaults={
                        'asin': r['asin'], 'product_name': r['product_name'], 'available_quantity': r['available_quantity']
                    })

                # 3. Amazon Orders
                df_ao = get_df('amazon_orders.xlsx')
                for _, r in df_ao.iterrows():
                    order, _ = AmazonOrder.objects.update_or_create(amazon_order_id=r['amazon_order_id'], defaults={
                        'user': user, 'purchase_date': timezone.now(), 'order_status': r['order_status'], 'order_total_amount': r['order_total_amount']
                    })
                    if r.get('order_item_id'):
                        AmazonOrderItem.objects.get_or_create(order_item_id=r['order_item_id'], defaults={
                            'order': order, 'asin': r['item_asin'], 'sku': r['item_sku'], 'title': r['item_title'], 
                            'quantity_ordered': r['quantity_ordered'], 'item_price_amount': r['item_price']
                        })

                # 4. Noon Products
                df_np = get_df('noon_products.xlsx')
                for _, r in df_np.iterrows():
                    NoonProduct.objects.update_or_create(noon_sku=r['noon_sku'], defaults={
                        'user': user, 'partner_sku': r['partner_sku'], 'title': r['title'], 'price': r['price'], 'stock_quantity': r['stock_quantity'], 'status': 'active'
                    })

                # 5. Noon Inventory (NEW)
                df_ni = get_df('noon_inventory.xlsx')
                for _, r in df_ni.iterrows():
                    NoonInventory.objects.update_or_create(partner_sku=r['partner_sku'], user=user, defaults={
                        'noon_sku': r['noon_sku'], 'barcode': r['barcode'], 'quantity': r['quantity']
                    })

                # 6. Noon Orders
                df_no = get_df('noon_orders.xlsx')
                for _, r in df_no.iterrows():
                    order, _ = NoonOrder.objects.update_or_create(order_nr=r['order_nr'], defaults={
                        'user': user, 'order_date': timezone.now(), 'status': r['status'], 'total_amount': r['total_amount']
                    })
                    if r.get('order_item_id'):
                        NoonOrderItem.objects.get_or_create(order_item_id=r['order_item_id'], defaults={
                            'order': order, 'noon_sku': r['item_noon_sku'], 'partner_sku': r['item_partner_sku'], 
                            'name': r['item_name'], 'quantity': r['quantity'], 'unit_price': r['unit_price'], 'total_price': r['total_price']
                        })

                self.stdout.write(self.style.SUCCESS("✅ ALL data (Products, Orders, Inventory) restored!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Restore failed: {str(e)}"))