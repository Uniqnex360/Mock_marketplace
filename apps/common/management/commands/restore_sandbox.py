import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

class Command(BaseCommand):
    help = 'Mirrors the local database snapshot to Render safely'

    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️  STARTING DATABASE MIRRORING...")

        # 1. Run migrations first to create all tables
        self.stdout.write("⚙️  Running migrations...")
        call_command('migrate', interactive=False)

        # 2. Check if tables exist before trying to delete
        # This prevents the "no such table" error
        all_tables = connection.introspection.table_names()
        
        if "amazon_ae_amazonorder" in all_tables:
            self.stdout.write("🧹 Cleaning existing data...")
            from apps.amazon_ae.models import AmazonOrder, AmazonProduct
            from apps.noon_ae.models import NoonOrder, NoonProduct
            from django.contrib.auth.models import User
            
            # Clear data to ensure the snapshot loads into a clean state
            AmazonOrder.objects.all().delete()
            AmazonProduct.objects.all().delete()
            NoonOrder.objects.all().delete()
            NoonProduct.objects.all().delete()
            User.objects.all().delete()

        # 3. Path to the snapshot
        snapshot_path = os.path.join(settings.BASE_DIR, 'data_source', 'snapshot.json')
        
        if os.path.exists(snapshot_path):
            self.stdout.write(f"📥 Loading snapshot from {snapshot_path}...")
            try:
                # loaddata will now restore Users, Tokens, Orders, and Products exactly
                call_command('loaddata', snapshot_path)
                self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Render is now an exact clone of your local DB!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error loading data: {e}"))
        else:
            self.stdout.write(self.style.ERROR("❌ Snapshot file missing in data_source/ folder!"))