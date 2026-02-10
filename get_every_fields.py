import json
import os

def list_all_keys(filename):
    with open(f'mongodb_full_backup/{filename}.json', 'r') as f:
        data = json.load(f)
    keys = set()
    for item in data:
        keys.update(item.keys())
    print(f"🔑 Fields in {filename}: {sorted(list(keys))}")

list_all_keys('product')
list_all_keys('order')
list_all_keys('order_items')