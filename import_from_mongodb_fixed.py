import pymongo
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import random
import os
from bson import ObjectId

# MongoDB connection from MarketLink project
MONGODB_URI = 'mongodb+srv://techteam:WcblsEme1Q1Vv7Rt@cluster0.5hrxigl.mongodb.net/ecommerce_db?retryWrites=true&w=majority&appName=Cluster0'

class MongoDBDataImporter:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['ecommerce_db']
        
        # AED conversion rate
        self.usd_to_aed = 3.67
        
        # UAE data for localization
        self.uae_cities = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah']
        self.uae_names = [
            ('Ahmed', 'Ali'), ('Fatima', 'Hassan'), ('Mohammed', 'Ibrahim'),
            ('Sara', 'Abdullah'), ('Omar', 'Khalid'), ('Aisha', 'Mohammed'),
            ('Khalid', 'Rashid'), ('Noura', 'Salem'), ('Hassan', 'Ahmad')
        ]
    
    def extract_and_transform_products(self):
        """Extract products from MongoDB and transform for both Amazon AE and Noon AE"""
        product_collection = self.db['product']
        products = list(product_collection.find().limit(1000))
        
        amazon_products = []
        noon_products = []
        
        print(f"📦 Found {len(products)} products in MongoDB")
        
        for idx, product in enumerate(products):
            # Convert price to AED if needed
            price = float(product.get('price', 0))
            if product.get('currency', '$') == '$':
                price = price * self.usd_to_aed
            
            # Common fields
            title = product.get('product_title', 'Unknown Product')
            brand = product.get('brand_name', product.get('manufacturer_name', 'Generic'))
            quantity = int(product.get('quantity', 0))
            image_url = product.get('image_url', '')
            if not image_url and product.get('image_urls'):
                image_url = product['image_urls'][0] if product['image_urls'] else ''
            
            # Split products between Amazon and Noon (50/50)
            if idx % 2 == 0:
                # Amazon AE format
                amazon_product = {
                    'asin': product.get('product_id', f"B{random.randint(100000000, 999999999)}"),
                    'sku': product.get('sku', f"SKU-{idx}"),
                    'title': title,
                    'description': product.get('product_description', ''),
                    'brand': brand,
                    'category': product.get('category', 'General'),
                    'price': round(price, 2),
                    'currency': 'AED',
                    'quantity': quantity,
                    'image_url': image_url,
                    'status': 'ACTIVE' if quantity > 0 else 'INACTIVE'
                }
                amazon_products.append(amazon_product)
            else:
                # Noon AE format
                noon_product = {
                    'noon_sku': f"N-{product.get('sku', f'SKU{idx}')}",
                    'partner_sku': product.get('sku', f"PART-{idx}"),
                    'title': title,
                    'title_ar': f"منتج {idx}",
                    'summary': product.get('product_description', '')[:500] if product.get('product_description') else '',
                    'brand': brand,
                    'category_code': self._map_category_to_noon(product.get('category', 'general')),
                    'product_type': product.get('product_type', 'General'),
                    'model_number': f"MODEL-{random.randint(1000, 9999)}",
                    'price': round(price, 2),
                    'sale_price': round(price * 0.9, 2) if random.random() < 0.3 else None,
                    'warranty': random.choice(['6 Months', '1 Year', '2 Years', 'No Warranty']),
                    'stock_quantity': quantity,
                    'max_order_quantity': min(10, quantity) if quantity > 0 else 10,
                    'status': 'active' if quantity > 0 else 'inactive',
                    'image_url': image_url
                }
                noon_products.append(noon_product)
        
        return amazon_products, noon_products
    
    def extract_and_transform_orders(self):
        """Extract orders and transform for both marketplaces"""
        order_collection = self.db['order']
        order_items_collection = self.db['order_items']
        
        # First, let's check the structure of order_items
        sample_item = order_items_collection.find_one()
        print(f"🔍 Sample order item fields: {list(sample_item.keys()) if sample_item else 'No items found'}")
        
        # Get all order items first
        all_order_items = list(order_items_collection.find().limit(1000))
        print(f"📦 Found {len(all_order_items)} order items")
        
        # Group items by order_id
        order_items_map = {}
        for item in all_order_items:
            order_id = item.get('order_id', '')
            if order_id not in order_items_map:
                order_items_map[order_id] = []
            order_items_map[order_id].append(item)
        
        amazon_orders = []
        noon_orders = []
        
        # Process orders based on order items
        for idx, (order_id, items) in enumerate(list(order_items_map.items())[:500]):
            if not items:
                continue
                
            # Generate UAE customer data
            customer = random.choice(self.uae_names)
            city = random.choice(self.uae_cities)
            
            # Create order date (last 30 days)
            days_ago = random.randint(0, 30)
            order_date = datetime.now() - timedelta(days=days_ago)
            
            # Process first item
            item = items[0]
            
            # Get price and convert to AED
            unit_price = float(item.get('unit_price', item.get('price', 100)))
            if unit_price < 1:  # Likely a percentage, use a default
                unit_price = 100
                
            # Check currency and convert
            currency = item.get('currency', '$')
            if currency == '$' or currency == 'USD':
                unit_price = unit_price * self.usd_to_aed
            
            quantity = int(item.get('quantity', 1))
            total_price = unit_price * quantity
            
            if idx % 2 == 0:
                # Amazon AE order
                amazon_order = {
                    'amazon_order_id': f"408-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}",
                    'purchase_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'order_status': random.choice(['Shipped', 'Delivered', 'Processing']),
                    'order_total_amount': round(total_price, 2),
                    'order_total_currency': 'AED',
                    'buyer_email': f"{customer[0].lower()}.{customer[1].lower()}@email.ae",
                    'buyer_name': f"{customer[0]} {customer[1]}",
                    'order_item_id': f"ITEM-{idx}-1",
                    'item_asin': item.get('product_id', f"B{random.randint(100000000, 999999999)}"),
                    'item_sku': item.get('sku', f'SKU-{idx}'),
                    'item_title': item.get('product_name', item.get('title', 'Product')),
                    'quantity_ordered': quantity,
                    'item_price': round(unit_price, 2)
                }
                amazon_orders.append(amazon_order)
            else:
                # Noon AE order
                noon_order = {
                    'order_nr': f"N-{order_date.year}-{random.randint(100000, 999999)}",
                    'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': random.choice(['confirmed', 'shipped', 'delivered']),
                    'customer_first_name': customer[0],
                    'customer_last_name': customer[1],
                    'customer_email': f"{customer[0].lower()}.{customer[1].lower()}@email.ae",
                    'customer_phone': f"+971{random.choice(['50', '52', '54', '56'])}{random.randint(1000000, 9999999)}",
                    'payment_method': random.choice(['credit_card', 'COD', 'debit_card']),
                    'total_amount': round(total_price, 2),
                    'currency': 'AED',
                    'delivery_provider': random.choice(['Noon Express', 'Aramex']),
                    'tracking_number': f"NE{random.randint(10000000, 99999999)}",
                    'address_city': city,
                    'order_item_id': f"N-ITEM-{idx}-1",
                    'item_noon_sku': f"N-{item.get('sku', f'SKU-{idx}')}",
                    'item_partner_sku': item.get('sku', f'PART-{idx}'),
                    'item_name': item.get('product_name', item.get('title', 'Product')),
                    'quantity': quantity,
                    'unit_price': round(unit_price, 2),
                    'total_price': round(total_price, 2),
                    'item_status': 'confirmed'
                }
                noon_orders.append(noon_order)
        
        # Also use custom_order collection if available
        custom_order_collection = self.db['custom_order']
        custom_orders = list(custom_order_collection.find().limit(100))
        print(f"📋 Found {len(custom_orders)} custom orders")
        
        for idx, order in enumerate(custom_orders):
            if order.get('ordered_products'):
                product = order['ordered_products'][0]
                
                # Generate UAE customer data
                customer = random.choice(self.uae_names)
                
                # Use order date from the document
                order_date = order.get('purchase_order_date', datetime.now())
                
                # Get price in AED
                unit_price = float(product.get('unit_price', 100))
                if order.get('currency') == 'USD' or order.get('currency') == 'INR':
                    unit_price = unit_price * self.usd_to_aed
                
                if len(amazon_orders) < 250:
                    amazon_order = {
                        'amazon_order_id': order.get('order_id', f"408-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}"),
                        'purchase_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'order_status': self._map_order_status_amazon(order.get('order_status', 'Pending')),
                        'order_total_amount': round(float(order.get('total_price', unit_price)), 2),
                        'order_total_currency': 'AED',
                        'buyer_email': order.get('mail', f"{customer[0].lower()}@email.ae"),
                        'buyer_name': order.get('customer_name', f"{customer[0]} {customer[1]}"),
                        'order_item_id': f"ITEM-CUSTOM-{idx}",
                        'item_asin': product.get('product_id', f"B{random.randint(100000000, 999999999)}"),
                        'item_sku': product.get('sku', 'SKU-CUSTOM'),
                        'item_title': product.get('title', 'Product'),
                        'quantity_ordered': product.get('quantity', 1),
                        'item_price': round(unit_price, 2)
                    }
                    amazon_orders.append(amazon_order)
                else:
                    noon_order = {
                        'order_nr': order.get('customer_order_id', f"N-{order_date.year}-{random.randint(100000, 999999)}"),
                        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': self._map_order_status_noon(order.get('order_status', 'Pending')),
                        'customer_first_name': order.get('customer_name', customer[0]).split()[0],
                        'customer_last_name': order.get('customer_name', f"{customer[0]} {customer[1]}").split()[-1],
                        'customer_email': order.get('mail', f"{customer[0].lower()}@email.ae"),
                        'customer_phone': order.get('contact_number', f"+971{random.choice(['50', '52'])}{random.randint(1000000, 9999999)}"),
                        'payment_method': order.get('payment_mode', 'COD'),
                        'total_amount': round(float(order.get('total_price', unit_price)), 2),
                        'currency': 'AED',
                        'delivery_provider': order.get('carrier', 'Noon Express'),
                        'tracking_number': order.get('tracking_number', f"NE{random.randint(10000000, 99999999)}"),
                        'address_city': order.get('shipping_address', 'Dubai').split(',')[-1].strip() if ',' in order.get('shipping_address', '') else 'Dubai',
                        'order_item_id': f"N-ITEM-CUSTOM-{idx}",
                        'item_noon_sku': f"N-{product.get('sku', 'SKU')}",
                        'item_partner_sku': product.get('sku', 'PART-SKU'),
                        'item_name': product.get('title', 'Product'),
                        'quantity': product.get('quantity', 1),
                        'unit_price': round(unit_price, 2),
                        'total_price': round(unit_price * product.get('quantity', 1), 2),
                        'item_status': 'confirmed'
                    }
                    noon_orders.append(noon_order)
        
        return amazon_orders, noon_orders
    
    def _map_order_status_amazon(self, status):
        """Map order status to Amazon format"""
        status_lower = status.lower()
        if 'deliver' in status_lower:
            return 'Delivered'
        elif 'ship' in status_lower:
            return 'Shipped'
        elif 'process' in status_lower or 'open' in status_lower:
            return 'Processing'
        elif 'cancel' in status_lower:
            return 'Cancelled'
        else:
            return 'Pending'
    
    def _map_order_status_noon(self, status):
        """Map order status to Noon format"""
        status_lower = status.lower()
        if 'deliver' in status_lower:
            return 'delivered'
        elif 'ship' in status_lower:
            return 'shipped'
        elif 'confirm' in status_lower or 'open' in status_lower:
            return 'confirmed'
        elif 'cancel' in status_lower:
            return 'cancelled'
        else:
            return 'placed'
    
    def create_inventory_from_products(self, amazon_products, noon_products):
        """Create inventory data from products"""
        amazon_inventory = []
        noon_inventory = []
        
        # Amazon inventory
        for product in amazon_products:
            inv = {
                'asin': product['asin'],
                'sku': product['sku'],
                'product_name': product['title'],
                'available_quantity': product['quantity'],
                'pending_quantity': random.randint(0, 5),
                'reserved_quantity': random.randint(0, 3),
                'total_quantity': product['quantity'] + random.randint(0, 10),
                'condition': 'new',
                'warehouse_condition_code': 'SELLABLE'
            }
            amazon_inventory.append(inv)
        
        # Noon inventory
        for product in noon_products:
            inv = {
                'noon_sku': product['noon_sku'],
                'partner_sku': product['partner_sku'],
                'barcode': f"{random.randint(1000000000000, 9999999999999)}",
                'quantity': product['stock_quantity'],
                'reserved_quantity': random.randint(0, 10),
                'warehouse_code': random.choice(['DXB-01', 'DXB-02', 'AUH-01'])
            }
            noon_inventory.append(inv)
        
        return amazon_inventory, noon_inventory
    
    def _map_category_to_noon(self, category):
        """Map categories to Noon format"""
        mapping = {
            'Electronics': 'electronics_computers',
            'Home & Kitchen': 'home_kitchen',
            'Beauty': 'beauty_health',
            'Sports': 'sports_outdoor',
            'Fashion': 'fashion_clothing',
            'Toys': 'toys_games',
            'Lawn & Patio': 'home_garden'
        }
        return mapping.get(category, 'general_merchandise')
    
    def save_to_excel(self):
        """Extract all data and save to Excel files"""
        print("🚀 Starting data extraction from MongoDB...")
        
        # Extract and transform products
        amazon_products, noon_products = self.extract_and_transform_products()
        
        # Extract and transform orders
        amazon_orders, noon_orders = self.extract_and_transform_orders()
        
        # Create inventory data
        amazon_inventory, noon_inventory = self.create_inventory_from_products(
            amazon_products, noon_products
        )
        
        # Create output directory
        output_dir = 'mongodb_imports'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to Excel files
        print("\n💾 Saving to Excel files...")
        
        # Amazon AE files
        pd.DataFrame(amazon_products).to_excel(f'{output_dir}/amazon_ae_products.xlsx', index=False)
        pd.DataFrame(amazon_orders).to_excel(f'{output_dir}/amazon_ae_orders.xlsx', index=False)
        pd.DataFrame(amazon_inventory).to_excel(f'{output_dir}/amazon_ae_inventory.xlsx', index=False)
        
        # Noon AE files
        pd.DataFrame(noon_products).to_excel(f'{output_dir}/noon_ae_products.xlsx', index=False)
        pd.DataFrame(noon_orders).to_excel(f'{output_dir}/noon_ae_orders.xlsx', index=False)
        pd.DataFrame(noon_inventory).to_excel(f'{output_dir}/noon_ae_inventory.xlsx', index=False)
        
        print("\n✅ Data extraction complete!")
        print(f"\n📊 Summary:")
        print(f"Amazon AE: {len(amazon_products)} products, {len(amazon_orders)} orders")
        print(f"Noon AE: {len(noon_products)} products, {len(noon_orders)} orders")
        print(f"\n📁 Files saved in: {output_dir}/")
        
        return output_dir
    
    def close(self):
        self.client.close()

if __name__ == "__main__":
    importer = MongoDBDataImporter()
    
    try:
        output_dir = importer.save_to_excel()
        
        print("\n📤 To upload to your Mock API, run: ./upload_imported_data.sh")
        
    finally:
        importer.close()