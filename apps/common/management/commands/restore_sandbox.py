import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.amazon_ae.models import AmazonProduct

class Command(BaseCommand):
    help = 'Mirrors the local database snapshot to Render'

    def handle(self, *args, **kwargs):
        self.stdout.write("🏗️  Starting Database Mirroring...")
        
        # 1. Run migrations to ensure tables exist
        call_command('migrate', interactive=False)
        
        # 2. Path to the snapshot
        snapshot_path = os.path.join(settings.BASE_DIR, 'data_source', 'snapshot.json')
        
        if os.path.exists(snapshot_path):
            self.stdout.write("📥 Loading local snapshot into Render...")
            
            # Use 'loaddata' to import the exact state of your local DB
            # We use ignorenonexistent to skip any fields that might differ slightly
            call_command('loaddata', snapshot_path)
            
            self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Render is now an exact mirror of your local machine!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Snapshot not found at {snapshot_path}"))