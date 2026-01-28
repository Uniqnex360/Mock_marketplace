#!/bin/bash

# Configuration
AMAZON_ID="amazon_ae_yVkOidNBLFFQ0Lum0RhYSg"
AMAZON_SECRET="ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
NOON_ID="noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw"
NOON_SECRET="Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"

API_URL="https://mock-marketplace.onrender.com"
DATA_DIR="render_upload_files"

echo "🚀 Uploading data to LIVE RENDER SERVER..."

# 1. Amazon Products
echo "📦 Uploading Amazon Products..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_ID" \
  -H "X-Client-Secret: $AMAZON_SECRET" \
  -F "file=@$DATA_DIR/amazon_products.xlsx" \
  -F "data_type=products"

# 2. Amazon Orders
echo -e "\n📦 Uploading Amazon Orders..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_ID" \
  -H "X-Client-Secret: $AMAZON_SECRET" \
  -F "file=@$DATA_DIR/amazon_orders.xlsx" \
  -F "data_type=orders"

# 3. Amazon Inventory
echo -e "\n📦 Uploading Amazon Inventory..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_ID" \
  -H "X-Client-Secret: $AMAZON_SECRET" \
  -F "file=@$DATA_DIR/amazon_inventory.xlsx" \
  -F "data_type=inventory"

# 4. Noon Products
echo -e "\n🌙 Uploading Noon Products..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_ID" \
  -H "X-Client-Secret: $NOON_SECRET" \
  -F "file=@$DATA_DIR/noon_products.xlsx" \
  -F "data_type=products"

# 5. Noon Orders
echo -e "\n🌙 Uploading Noon Orders..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_ID" \
  -H "X-Client-Secret: $NOON_SECRET" \
  -F "file=@$DATA_DIR/noon_orders.xlsx" \
  -F "data_type=orders"

# 6. Noon Inventory
echo -e "\n🌙 Uploading Noon Inventory..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_ID" \
  -H "X-Client-Secret: $NOON_SECRET" \
  -F "file=@$DATA_DIR/noon_inventory.xlsx" \
  -F "data_type=inventory"

echo -e "\n\n✅ Live Upload Complete!"
