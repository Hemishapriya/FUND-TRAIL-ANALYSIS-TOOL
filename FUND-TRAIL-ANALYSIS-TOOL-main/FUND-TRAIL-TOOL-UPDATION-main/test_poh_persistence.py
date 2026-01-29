from app import app, db
from models import POHRefundDetails
import sys

# Simulation of the user's workflow:
# 1. Initial Save
# 2. Edit (Update)
# 3. Persistence Check

def test_persistence():
    with app.app_context():
        # Clean up any existing test data
        ack_no = "TEST_ACK_001"
        txn_id = "TEST_TXN_001"
        
        # Ensure cleanup first
        existing = POHRefundDetails.query.filter_by(ack_no=ack_no, txn_id=txn_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print("Cleaned up old test data.")

        print("\n--- Step 1: Initial Save ---")
        # Simulate saving for the first time
        new_entry = POHRefundDetails(
            ack_no=ack_no,
            txn_id=txn_id,
            court_order_date="01-01-2024",
            refund_status="Refunded",
            refund_amount=5000.0
        )
        db.session.add(new_entry)
        db.session.commit()
        print("Initial data saved.")

        # Verify
        saved = POHRefundDetails.query.filter_by(ack_no=ack_no, txn_id=txn_id).first()
        print(f"Verified Saved Data: Status={saved.refund_status}, Amount={saved.refund_amount}")
        assert saved.refund_status == "Refunded"
        assert saved.refund_amount == 5000.0

        print("\n--- Step 2: Edit (Update) ---")
        # Simulate user editing the data
        # Logic matches save_hold_refund
        to_update = POHRefundDetails.query.filter_by(ack_no=ack_no, txn_id=txn_id).first()
        if to_update:
            to_update.court_order_date = "02-02-2025"
            to_update.refund_status = "Partial Refund"
            to_update.refund_amount = 2500.0
            db.session.commit()
            print("Data updated.")
        
        # Verify
        updated = POHRefundDetails.query.filter_by(ack_no=ack_no, txn_id=txn_id).first()
        print(f"Verified Updated Data: Status={updated.refund_status}, Amount={updated.refund_amount}")
        assert updated.refund_status == "Partial Refund"
        assert updated.refund_amount == 2500.0
        assert updated.court_order_date == "02-02-2025"

        print("\n--- Step 3: Persistence Check ---")
        # In a real app restart, we'd lose memory, but here we query the DB file again.
        # Since we are using the 'poh_store' bind, it reads from the SQLite file.
        # This confirms it's in the file.
        
        check = POHRefundDetails.query.filter_by(ack_no=ack_no, txn_id=txn_id).first()
        if check:
            print("SUCCESS: Data persisted in SQLite file correctly.")
        else:
            print("FAILURE: Data not found.")

        # Cleanup
        db.session.delete(check)
        db.session.commit()
        print("\nTest completed successfully.")

if __name__ == "__main__":
    test_persistence()
