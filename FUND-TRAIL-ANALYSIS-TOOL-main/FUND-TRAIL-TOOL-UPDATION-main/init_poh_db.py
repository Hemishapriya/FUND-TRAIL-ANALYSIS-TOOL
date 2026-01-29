from app import app, db
import os

with app.app_context():
    print("Creating tables for all binds...")
    db.create_all()
    
    poh_db_path = os.path.join(app.root_path, 'poh_refund_details.db')
    print(f"Checking for file at: {poh_db_path}")
    
    if os.path.exists(poh_db_path):
        print(f"SUCCESS: Database file created at {poh_db_path}")
    else:
        print("ERROR: Database file NOT found in project root.")
