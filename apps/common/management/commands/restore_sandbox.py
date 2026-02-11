import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️  MIRRORING LOCAL DATABASE...")
        
        # 1. Clear existing data to avoid primary key conflicts
        from apps.amazon_ae.models import AmazonOrder, AmazonProduct
        from apps.noon_ae.models import NoonOrder, NoonProduct
        from django.contrib.auth.models import User
        
        AmazonOrder.objects.all().delete()
        AmazonProduct.objects.all().delete()
        NoonOrder.objects.all().delete()
        NoonProduct.objects.all().delete()

        # 2. Path to the snapshot you just created
        snapshot_path = os.path.join(settings.BASE_DIR, 'data_source', 'snapshot.json')
        
        if os.path.exists(snapshot_path):
            self.stdout.write("📥 Loading Snapshot...")
            # loaddata is the standard Django way to import a DB dump
            call_command('loaddata', snapshot_path)
            self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Render is now an exact clone of your local DB!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Snapshot file missing!"))