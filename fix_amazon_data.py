import pandas as pd
import os

# Read existing Amazon files
amazon_products = pd.read_excel('mongodb_imports/amazon_ae_products.xlsx')
amazon_inventory = pd.read_excel('mongodb_imports/amazon_ae_inventory.xlsx')

# Fix NULL/empty values in products
amazon_products['description'] = amazon_products['description'].fillna('')
amazon_products['description'] = amazon_products['description'].apply(lambda x: str(x) if x else 'No description available')

# Fix NULL/empty values in inventory
amazon_inventory['asin'] = amazon_inventory['asin'].fillna('')
amazon_inventory['asin'] = amazon_inventory['asin'].apply(lambda x: str(x) if x else 'UNKNOWN')

# Ensure all required fields have values
for col in ['sku', 'title', 'brand', 'category']:
    if col in amazon_products.columns:
        amazon_products[col] = amazon_products[col].fillna('Unknown')

for col in ['sku', 'product_name']:
    if col in amazon_inventory.columns:
        amazon_inventory[col] = amazon_inventory[col].fillna('Unknown')

# Save fixed files
amazon_products.to_excel('mongodb_imports/amazon_ae_products_fixed.xlsx', index=False)
amazon_inventory.to_excel('mongodb_imports/amazon_ae_inventory_fixed.xlsx', index=False)

print("✅ Fixed Amazon data files created!")
print(f"Products: {len(amazon_products)} items")
print(f"Inventory: {len(amazon_inventory)} items")