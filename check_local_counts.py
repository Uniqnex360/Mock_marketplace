import json
import os

BACKUP_FOLDER = "mongodb_full_backup"

def check_local_backup_counts():
    if not os.path.exists(BACKUP_FOLDER):
        print(f"❌ Error: Folder '{BACKUP_FOLDER}' not found!")
        return

    # Get all JSON files in the folder
    files = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.json')]
    
    if not files:
        print("Empty folder. No JSON backups found.")
        return

    print("\n" + "="*45)
    print(f"{'COLLECTION (JSON FILE)':<28} | {'COUNT':<10}")
    print("="*45)

    total_docs = 0
    for filename in sorted(files):
        file_path = os.path.join(BACKUP_FOLDER, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Since we saved them as lists of objects
                count = len(data) if isinstance(data, list) else 1
                
            # Remove '.json' for the display name
            display_name = filename.replace('.json', '')
            print(f"{display_name:<28} | {count:<10,}")
            total_docs += count
        except Exception as e:
            print(f"{filename:<28} | ERROR: {str(e)}")

    print("="*45)
    print(f"{'TOTAL LOCAL RECORDS':<28} | {total_docs:<10,}")
    print("="*45 + "\n")

if __name__ == "__main__":
    check_local_backup_counts()
