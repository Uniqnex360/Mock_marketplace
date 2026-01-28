import pandas as pd

# Read the fixed Amazon products file
df = pd.read_excel('mongodb_imports/amazon_ae_products_fixed.xlsx')

# Ensure all fields have proper defaults
df['image_url'] = df['image_url'].fillna('')
df['description'] = df['description'].fillna('No description available')
df['brand'] = df['brand'].fillna('Generic')
df['category'] = df['category'].fillna('General')
df['currency'] = df['currency'].fillna('AED')
df['status'] = df['status'].fillna('ACTIVE')

# Ensure numeric fields
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)

# Remove any completely empty rows
df = df.dropna(subset=['asin', 'sku', 'title'], how='all')

# Save the final fixed file
df.to_excel('mongodb_imports/amazon_ae_products_final.xlsx', index=False)

print(f"✅ Fixed Amazon products file created with {len(df)} products")
print("\nSample data:")
print(df[['asin', 'sku', 'title', 'price', 'image_url']].head())