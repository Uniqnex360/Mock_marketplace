import pandas as pd
import random
from datetime import datetime, timedelta

# Read Noon products
noon_products = pd.read_excel('mongodb_imports/noon_ae_products.xlsx')

# Generate Noon orders
noon_orders = []
uae_names = [
    ('Ahmed', 'Ali'), ('Fatima', 'Hassan'), ('Mohammed', 'Ibrahim'),
    ('Sara', 'Abdullah'), ('Omar', 'Khalid'), ('Aisha', 'Mohammed'),
    ('Khalid', 'Rashid'), ('Noura', 'Salem'), ('Hassan', 'Ahmad')
]
uae_cities = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah']

# Generate 50 orders
for i in range(50):
    # Pick a random product
    product = noon_products.sample(1).iloc[0]
    customer = random.choice(uae_names)
    city = random.choice(uae_cities)
    
    # Create order date in last 30 days
    days_ago = random.randint(0, 30)
    order_date = datetime.now() - timedelta(days=days_ago)
    
    quantity = random.randint(1, 3)
    unit_price = float(product['price'])
    
    order = {
        'order_nr': f"N-2024-{random.randint(100000, 999999)}",
        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'status': random.choice(['confirmed', 'shipped', 'delivered', 'placed']),
        'customer_first_name': customer[0],
        'customer_last_name': customer[1],
        'customer_email': f"{customer[0].lower()}.{customer[1].lower()}@email.ae",
        'customer_phone': f"+971{random.choice(['50', '52', '54', '56'])}{random.randint(1000000, 9999999)}",
        'payment_method': random.choice(['credit_card', 'COD', 'debit_card', 'apple_pay']),
        'total_amount': round(unit_price * quantity, 2),
        'currency': 'AED',
        'delivery_provider': random.choice(['Noon Express', 'Aramex', 'Fetchr']),
        'tracking_number': f"NE{random.randint(10000000, 99999999)}",
        'address_city': city,
        'address_area': random.choice(['Downtown', 'Marina', 'JBR', 'Business Bay']),
        'address_street': f"Street {random.randint(1, 50)}, Building {random.randint(1, 100)}",
        'is_express': random.choice([True, False]),
        'order_item_id': f"N-ITEM-{i+1}",
        'item_noon_sku': product['noon_sku'],
        'item_partner_sku': product['partner_sku'],
        'item_name': product['title'],
        'quantity': quantity,
        'unit_price': unit_price,
        'total_price': round(unit_price * quantity, 2),
        'item_status': 'confirmed'
    }
    noon_orders.append(order)

# Save to Excel
pd.DataFrame(noon_orders).to_excel('mongodb_imports/noon_ae_orders.xlsx', index=False)
print(f"✅ Generated {len(noon_orders)} Noon orders!")