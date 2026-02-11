import os, django, json

# --- DJANGO SETUP ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_mock.settings')
django.setup()

from apps.amazon_ae.models import AmazonOrder, AmazonOrderItem, AmazonProduct
from apps.noon_ae.models import NoonOrder, NoonOrderItem, NoonProduct

def clean_id(val):
    """Removes our test prefixes and suffixes to find original MongoDB ID"""
    if not val: return ""
    return str(val).replace('999-', '').replace('Z-', '').replace('-X', '').strip()

def get_mongo_product_map():
    """Builds a map indexed by ASIN, SKU, and Product_ID for 100% match rate"""
    path = 'mongodb_full_backup/product.json'
    super_map = {}
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            for p in data:
                # Index this record by every possible identifier it has
                identifiers = [p.get('asin'), p.get('product_id'), p.get('sku'), p.get('master_sku')]
                for ident in identifiers:
                    if ident:
                        super_map[str(ident).strip()] = p
    return super_map

def enrich_amazon(prod_map):
    print("🚀 Enriching Amazon columns using Super-Match...")
    count = 0
    for p in AmazonProduct.objects.all():
        # Try to match current ASIN or current SKU (after cleaning)
        match = prod_map.get(clean_id(p.asin)) or prod_map.get(clean_id(p.sku))
        
        if match:
            p.product_title = match.get('product_title') or match.get('title')
            p.brand_name = match.get('brand_name')
            p.listing_quality_score = match.get('listing_quality_score', 0)
            p.product_cost = match.get('product_cost', 0)
            p.total_cogs = match.get('total_cogs', 0)
            p.attributes = match.get('attributes', {})
            p.save()
            count += 1
    print(f"✅ {count} Amazon Products enriched.")

def enrich_noon(prod_map):
    print("🚀 Enriching Noon columns using Super-Match...")
    count = 0
    for p in NoonProduct.objects.all():
        # Match by cleaned partner_sku or noon_sku
        match = prod_map.get(clean_id(p.partner_sku)) or prod_map.get(clean_id(p.noon_sku))
        
        if match:
            p.product_title = match.get('product_title') or match.get('title')
            p.brand_name = match.get('brand_name')
            p.listing_quality_score = match.get('listing_quality_score', 0)
            p.attributes = match.get('attributes', {})
            p.save()
            count += 1
    print(f"✅ {count} Noon Products enriched.")

if __name__ == "__main__":
    m_map = get_mongo_product_map()
    enrich_amazon(m_map)
    enrich_noon(m_map)
    print("\n🎉 SUPER-MATCH ENRICHMENT COMPLETE!")