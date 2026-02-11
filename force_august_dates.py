import os, django, random
from datetime import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder
from apps.noon_ae.models import NoonOrder

def fix_dates():
    print("📅 Forcing all order dates to August 2025...")
    
    # Fix Amazon
    for o in AmazonOrder.objects.all():
        day = random.randint(1, 31)
        o.purchase_date = timezone.make_aware(datetime(2025, 8, day, 12, 0, 0))
        o.save()
    
    # Fix Noon
    for o in NoonOrder.objects.all():
        day = random.randint(1, 31)
        o.order_date = timezone.make_aware(datetime(2025, 8, day, 15, 30, 0))
        o.save()

    print("✅ All local dates are now in August 2025.")

if __name__ == "__main__":
    fix_dates()