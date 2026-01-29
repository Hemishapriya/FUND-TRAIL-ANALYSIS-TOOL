
from app import app, db, Transaction
import os

def test_victim_letter_generation():
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        # Setup test client
        client = app.test_client()
        
        # Ensure we have a dummy transaction to fetch
        ack_no = "TEST_VICTIM_001"
        account_number = "9876543210" # Victim Account?
        
        # Check if exists, else create
        txn = Transaction.query.filter_by(ack_no=ack_no).first()
        if not txn:
            txn = Transaction(
                ack_no=ack_no,
                account_number="SOURCE_ACC",
                to_account=account_number, # If fetching by to_account
                amount=5000.0,
                txn_date="2025-01-20",
                txn_id="TXN12345",
                ifsc_code="SBIN0001234",
                bank_name="SBI",
                layer=1
            )
            db.session.add(txn)
            db.session.commit()
            print(f"Created test transaction for {ack_no}")
        
        payload = {
            "ack_no": ack_no, 
            "account_number": account_number,
            "letter_type": "victim",
            "is_poh": False,
            "officer_name": "Test Officer",
            "officer_designation": "Inspector",
            "officer_phone": "9876543210",
            "officer_email": "test@police.gov.in",
            "letter_date": "23-01-2026",
            "crime_no": "100/2026",
            "ncrp_ack_no": ack_no
        }
        
        # Need to handle CSRF? 
        # Usually test_client requires csrf_token if WTF_CSRF_CHECK_DEFAULT is True.
        # But let's try.
        
        print(f"Sending POST to /generate_letter_docx...")
        res = client.post('/generate_letter_docx', json=payload, follow_redirects=True)
        
        if res.status_code == 200:
            print("Success! File generated.")
            output_path = "test_victim_letter_output.docx"
            with open(output_path, "wb") as f:
                f.write(res.data)
            print(f"Saved response to {output_path}")
            
            # Optional: Inspect the generated docx to verify table content
            import docx
            doc = docx.Document(output_path)
            print("Inspecting generated file...")
            found_table = False
            for table in doc.tables:
                headers = [c.text.strip() for c in table.rows[0].cells]
                if "Victim Account Number" in headers:
                    found_table = True
                    print("Found Victim Table!")
                    if len(table.rows) > 1:
                        row_data = [c.text.strip() for c in table.rows[1].cells]
                        print(f"Row 1 Data: {row_data}")
                        # Expect: S No, Victim Acc, Date, Amt, TxnID, IFSC
                        # Logic: row[1] = t.to_account = account_number
                        if row_data[1] == account_number:
                            print("VERIFICATION PASSED: Account number matches.")
                        else:
                            print(f"VERIFICATION FAILED: Expected {account_number}, got {row_data[1]}")
                    else:
                        print("Table has no data rows.")
            if not found_table:
                print("VERIFICATION FAILED: Victim Table not found.")
                
        else:
            print(f"Failed: {res.status_code}")
            # print(res.data.decode())

if __name__ == "__main__":
    test_victim_letter_generation()
