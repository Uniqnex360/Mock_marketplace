#!/bin/bash

# paste your fresh token here
TOKEN="BjWZuxiHIpnmf7755bUZxgmyL4RJvFfCNVyoU5cMg-p-_l7Fp2Awx-5_Q5xtx-ukvYHucngsU7jbGA7B3hhSQw"

API_URL="https://mock-marketplace.onrender.com"
DATA_DIR="render_upload_files"

echo "🚀 Uploading data to LIVE RENDER SERVER using Bearer Token..."

# 1. Amazon Products
echo "📦 Uploading Amazon Products..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/amazon_products.xlsx" \
  -F "data_type=products"

# 2. Amazon Orders
echo -e "\n📦 Uploading Amazon Orders..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/amazon_orders.xlsx" \
  -F "data_type=orders"

# 3. Amazon Inventory
echo -e "\n📦 Uploading Amazon Inventory..."
curl -X POST $API_URL/api/upload/amazon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/amazon_inventory.xlsx" \
  -F "data_type=inventory"

# 4. Noon Products
echo -e "\n🌙 Uploading Noon Products..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/noon_products.xlsx" \
  -F "data_type=products"

# 5. Noon Orders
echo -e "\n🌙 Uploading Noon Orders..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/noon_orders.xlsx" \
  -F "data_type=orders"

# 6. Noon Inventory
echo -e "\n🌙 Uploading Noon Inventory..."
curl -X POST $API_URL/api/upload/noon/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$DATA_DIR/noon_inventory.xlsx" \
  -F "data_type=inventory"

echo -e "\n\n✅ Live Upload Complete!"
