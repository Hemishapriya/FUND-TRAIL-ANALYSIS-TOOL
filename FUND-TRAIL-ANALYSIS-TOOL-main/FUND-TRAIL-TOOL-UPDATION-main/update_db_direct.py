
import sqlite3
import os

db_path = 'fundtrail.db'

if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'must_change_password' in columns:
            print("Column 'must_change_password' already exists.")
        else:
            print("Adding column 'must_change_password'...")
            cursor.execute("ALTER TABLE user ADD COLUMN must_change_password BOOLEAN DEFAULT 0")
            conn.commit()
            print("Column added successfully.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
