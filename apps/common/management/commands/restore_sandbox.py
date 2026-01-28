import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from apps.authentication.models import MarketplaceCredential
from apps.amazon_ae.models import AmazonProduct
from apps.data_upload.views import (
    upload_amazon_products, upload_amazon_orders, upload_amazon_inventory,
    upload_noon_products, upload_noon_orders, upload_noon_inventory,
    run_fix_logic
)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️ Checking Sandbox State...")
        
        # 1. Run Migrations
        call_command('migrate', interactive=False)
        
        # 2. Setup User & Credentials
        user, _ = User.objects.get_or_create(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Force IDs to match documentation
        amz, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='AMAZON_AE')
        amz.client_id, amz.client_secret = "amazon_ae_yVkOidNBLFFQ0Lum0RhYSg", "ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
        amz.save()
        
        noon, _ = MarketplaceCredential.objects.get_or_create(user=user, marketplace='NOON_AE')
        noon.client_id, noon.client_secret = "noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw", "Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"
        noon.save()

        # 3. Import Data if missing
        if AmazonProduct.objects.count() == 0:
            self.stdout.write("📥 DB Empty. Restoring 1000+ records from data_source...")
            path = os.path.join(settings.BASE_DIR, 'data_source')
            
            try:
                upload_amazon_products(pd.read_excel(f"{path}/amazon_products.xlsx"), user)
                upload_amazon_orders(pd.read_excel(f"{path}/amazon_orders.xlsx"), user)
                upload_amazon_inventory(pd.read_excel(f"{path}/amazon_inventory.xlsx"), user)
                upload_noon_products(pd.read_excel(f"{path}/noon_products.xlsx"), user)
                upload_noon_orders(pd.read_excel(f"{path}/noon_orders.xlsx"), user)
                upload_noon_inventory(pd.read_excel(f"{path}/noon_inventory.xlsx"), user)
                run_fix_logic(user)
                self.stdout.write(self.style.SUCCESS("✅ Data Restored!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Import failed: {str(e)}"))
        else:
            self.stdout.write("✅ Data already present.")