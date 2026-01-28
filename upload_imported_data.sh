#!/bin/bash

# Configuration
AMAZON_CLIENT_ID="amazon_ae_yVkOidNBLFFQ0Lum0RhYSg"
AMAZON_CLIENT_SECRET="ITjP9X44IVgM-hJV9_Y62rwawmoMy4HkgF_eyhfacnA"
NOON_CLIENT_ID="noon_ae_Yr7BIPz3d0ZoRzvMGYeEUw"
NOON_CLIENT_SECRET="Q8RwmadK7YbwQ3iYLHP_sdGAWaVNw4Jc6CTv4dntgfU"
API_URL="http://localhost:8000"
DATA_DIR="mongodb_imports"

echo "📤 Uploading imported data to Mock Marketplace API..."

# Upload Amazon AE data
echo -e "\n🔸 Uploading Amazon AE products..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_CLIENT_ID" \
  -H "X-Client-Secret: $AMAZON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/amazon_ae_products.xlsx" \
  -F "data_type=products"

echo -e "\n\n🔸 Uploading Amazon AE orders..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_CLIENT_ID" \
  -H "X-Client-Secret: $AMAZON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/amazon_ae_orders.xlsx" \
  -F "data_type=orders"

echo -e "\n\n🔸 Uploading Amazon AE inventory..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "X-Client-ID: $AMAZON_CLIENT_ID" \
  -H "X-Client-Secret: $AMAZON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/amazon_ae_inventory.xlsx" \
  -F "data_type=inventory"

# Upload Noon AE data
echo -e "\n\n🔸 Uploading Noon AE products..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_CLIENT_ID" \
  -H "X-Client-Secret: $NOON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/noon_ae_products.xlsx" \
  -F "data_type=products"

echo -e "\n\n🔸 Uploading Noon AE orders..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_CLIENT_ID" \
  -H "X-Client-Secret: $NOON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/noon_ae_orders.xlsx" \
  -F "data_type=orders"

echo -e "\n\n🔸 Uploading Noon AE inventory..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "X-Client-ID: $NOON_CLIENT_ID" \
  -H "X-Client-Secret: $NOON_CLIENT_SECRET" \
  -F "file=@$DATA_DIR/noon_ae_inventory.xlsx" \
  -F "data_type=inventory"

echo -e "\n\n✅ Upload complete!"