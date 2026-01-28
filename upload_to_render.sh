#!/bin/bash

# Clean token only
TOKEN="PVsEYymQJyBoHwy_-kfynmUBcqxD08IlB28A6-Meqkc-hHp-IuNF0pdi9LuYUsJ3fGJL__KhkN2DKI3qzPfvfA"

API_URL="https://mock-marketplace.onrender.com"
DATA_DIR="render_upload_files"

echo "🚀 Uploading data to LIVE RENDER SERVER..."

# 1. Amazon Products
curl -X POST $API_URL/api/upload/amazon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/amazon_products.xlsx" -F "data_type=products"
# 2. Amazon Orders
curl -X POST $API_URL/api/upload/amazon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/amazon_orders.xlsx" -F "data_type=orders"
# 3. Amazon Inventory
curl -X POST $API_URL/api/upload/amazon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/amazon_inventory.xlsx" -F "data_type=inventory"
# 4. Noon Products
curl -X POST $API_URL/api/upload/noon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/noon_products.xlsx" -F "data_type=products"
# 5. Noon Orders
curl -X POST $API_URL/api/upload/noon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/noon_orders.xlsx" -F "data_type=orders"
# 6. Noon Inventory
curl -X POST $API_URL/api/upload/noon/ -H "Authorization: Bearer $TOKEN" -F "file=@$DATA_DIR/noon_inventory.xlsx" -F "data_type=inventory"

echo -e "\n\n✅ Live Upload Complete!"
