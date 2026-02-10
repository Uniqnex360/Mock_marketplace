import pymongo
from bson import json_util
import os

URI = "mongodb+srv://techteam:WcblsEme1Q1Vv7Rt@cluster0.5hrxigl.mongodb.net/ecommerce_db?retryWrites=true&w=majority"
BACKUP_FOLDER = "mongodb_full_backup"

def take_backup():
    print("🔗 Connecting to MongoDB...")
    client = pymongo.MongoClient(URI)
    db = client['ecommerce_db']
    
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
        
    collections = db.list_collection_names()
    print(f"📂 Found {len(collections)} collections. Starting copy...")

    for col_name in collections:
        print(f"📦 Copying: {col_name}...")
        data = list(db[col_name].find({}))
        
        with open(os.path.join(BACKUP_FOLDER, f"{col_name}.json"), 'w') as f:
            f.write(json_util.dumps(data, indent=2))
            
    print(f"\n✅ SUCCESS! All data saved in the '{BACKUP_FOLDER}' folder.")

if __name__ == "__main__":
    take_backup()
