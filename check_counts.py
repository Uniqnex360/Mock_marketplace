import pymongo

URI = "mongodb+srv://techteam:WcblsEme1Q1Vv7Rt@cluster0.5hrxigl.mongodb.net/ecommerce_db?retryWrites=true&w=majority&appName=Cluster0"

def check_all_counts():
    try:
        print("🔗 Connecting to MongoDB...")
        client = pymongo.MongoClient(URI)
        db = client['ecommerce_db']
        
        collections = db.list_collection_names()
        
        print("\n" + "="*40)
        print(f"{'COLLECTION NAME':<25} | {'COUNT':<10}")
        print("="*40)

        total_docs = 0
        # Sort collections alphabetically for better readability
        for col_name in sorted(collections):
            count = db[col_name].count_documents({})
            print(f"{col_name:<25} | {count:<10,}")
            total_docs += count
        
        print("="*40)
        print(f"{'TOTAL DOCUMENTS':<25} | {total_docs:<10,}")
        print("="*40)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    check_all_counts()
