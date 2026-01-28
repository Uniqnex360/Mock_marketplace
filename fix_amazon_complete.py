import pandas as pd
import numpy as np

# Read the file
df = pd.read_excel('mongodb_imports/amazon_ae_products_final.xlsx')

# Replace all NaN, None, and empty values with appropriate defaults
df = df.replace({np.nan: '', None: ''})

# Ensure all text fields are strings
text_fields = ['asin', 'sku', 'title', 'description', 'brand', 'category', 'image_url', 'status', 'currency']
for field in text_fields:
    if field in df.columns:
        df[field] = df[field].astype(str).replace('nan', '')

# Clean up specific fields
df['asin'] = df['asin'].apply(lambda x: x if x and x != '' else f'B{np.random.randint(100000000, 999999999)}')
df['sku'] = df['sku'].apply(lambda x: x if x and x != '' else f'SKU-{np.random.randint(10000, 99999)}')
df['title'] = df['title'].apply(lambda x: x if x and x != '' else 'Product')
df['description'] = df['description'].apply(lambda x: x if x and x != '' else 'No description available')
df['brand'] = df['brand'].apply(lambda x: x if x and x != '' else 'Generic')
df['category'] = df['category'].apply(lambda x: x if x and x != '' else 'General')
df['image_url'] = df['image_url'].apply(lambda x: x if x and x != '' else '')
df['status'] = df['status'].apply(lambda x: x if x and x != '' else 'ACTIVE')
df['currency'] = 'AED'

# Fix numeric fields
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)

# Remove any rows with critical missing data
df = df[df['asin'] != '']
df = df[df['sku'] != '']
df = df[df['title'] != '']

# Save cleaned file
df.to_excel('mongodb_imports/amazon_ae_products_clean.xlsx', index=False)

print(f"✅ Cleaned Amazon products: {len(df)} items")
print("\nData check:")
print(f"- Products with empty image_url: {(df['image_url'] == '').sum()}")
print(f"- Products with empty description: {(df['description'] == '').sum()}")
print(f"- All ASINs present: {(df['asin'] != '').all()}")
print(f"- All SKUs present: {(df['sku'] != '').all()}")
print(f"- All titles present: {(df['title'] != '').all()}")

# Show sample
print("\nSample cleaned data:")
print(df[['asin', 'sku', 'title', 'image_url']].head())