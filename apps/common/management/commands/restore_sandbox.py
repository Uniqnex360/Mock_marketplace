import os, json, random
import pandas as pd
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
    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️  Starting Full Restore & Relationship Fix...")
        call_command('migrate', interactive=False)
        
        user, _ = User.objects.get_or_create(username='testuser')
        user.set_password('testpass123')
        user.save()

        # 1. Credentials
        amz_c, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='AMAZON_AE')
        amz_c.client_id, amz_c.client_secret = "amazon_ae_yVkOidNBLFFQ0Lum0RhYSg", "ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
        amz_c.save()

        # 2. Import Data (Only if empty)
        if AmazonProduct.objects.count() == 0:
            path = os.path.join(settings.BASE_DIR, 'data_source')
            def get_df(name): return pd.read_excel(os.path.join(path, name)).where(pd.notnull, None)

            try:
                # Import Products
                df_ap = get_df('amazon_products.xlsx')
                for _, r in df_ap.iterrows():
                    AmazonProduct.objects.create(user=user, asin=r['asin'], sku=r['sku'], title=r['title'], price=r['price'], quantity=r['quantity'], status='ACTIVE')
                
                # Import Orders
                df_ao = get_df('amazon_orders.xlsx')
                for idx, r in df_ao.iterrows():
                    # Set historical date
                    hist_date = timezone.make_aware(datetime(2025, 8, (idx % 28) + 1, 12, 0, 0))
                    AmazonOrder.objects.create(user=user, amazon_order_id=r['amazon_order_id'], purchase_date=hist_date, order_status=r['order_status'], order_total_amount=r['order_total_amount'])

                # Import Noon Data (Simplified)
                df_np = get_df('noon_products.xlsx')
                for _, r in df_np.iterrows():
                    NoonProduct.objects.create(user=user, noon_sku=r['noon_sku'], partner_sku=r['partner_sku'], title=r['title'], price=r['price'], stock_quantity=r['stock_quantity'])
                
                df_no = get_df('noon_orders.xlsx')
                for idx, r in df_no.iterrows():
                    hist_date = timezone.make_aware(datetime(2025, 8, (idx % 28) + 1, 15, 0, 0))
                    NoonOrder.objects.create(user=user, order_nr=r['order_nr'], order_date=hist_date, status=r['status'], total_amount=r['total_amount'])

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Import error: {e}"))

        # 3. THE FIX: Ensure every order has at least one item
        self.stdout.write("🔗 Linking Order Items to real products...")
        all_amz_products = list(AmazonProduct.objects.all())
        all_noon_products = list(NoonProduct.objects.all())

        # Fix Amazon
        for order in AmazonOrder.objects.all():
            if order.items.count() == 0:
                p = random.choice(all_amz_products)
                AmazonOrderItem.objects.create(
                    order=order, order_item_id=f"ITEM-{order.amazon_order_id}",
                    asin=p.asin, sku=p.sku, title=p.title,
                    quantity_ordered=random.randint(1,2), item_price_amount=p.price
                )

        # Fix Noon
        for order in NoonOrder.objects.all():
            if order.items.count() == 0:
                p = random.choice(all_noon_products)
                NoonOrderItem.objects.create(
                    order=order, order_item_id=f"N-ITEM-{order.order_nr}",
                    noon_sku=p.noon_sku, partner_sku=p.partner_sku, name=p.title,
                    quantity=random.randint(1,2), unit_price=p.price, total_price=p.price, status=order.status
                )

        self.stdout.write(self.style.SUCCESS("✅ All orders now have linked items!"))