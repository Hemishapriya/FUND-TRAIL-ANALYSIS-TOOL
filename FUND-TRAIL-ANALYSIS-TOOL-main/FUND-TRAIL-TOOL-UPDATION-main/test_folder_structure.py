from app import app
import os
import shutil

def test_suspect_letter_folder():
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    
    ack_no = "TEST_FOLDER_CHECK"
    account_number = "2222222222"
    
    payload = {
        "ack_no": ack_no,
        "account_number": account_number,
        "letter_type": "suspect",
        "is_poh": True,
        "officer_name": "Officer X",
        "officer_designation": "SI",
        "officer_phone": "9999999999",
        "officer_email": "x@police.com",
        "ncrp_ack_no": ack_no
    }
    
    # Clean up previous test
    base_dir = os.path.join(app.root_path, 'generated_letters', ack_no)
    if os.path.exists(base_dir):
        try:
            shutil.rmtree(base_dir)
        except Exception as e:
            print(f"Warning: Could not delete {base_dir}: {e}")
        
    print(f"Sending request for ACK: {ack_no}")
    try:
        res = client.post('/generate_letter_docx', json=payload, follow_redirects=True)
        
        if res.status_code == 200:
            print("Response 200 OK")
            
            # Check folder structure
            expected_dir = os.path.join(app.root_path, 'generated_letters', ack_no, 'suspect letter')
            expected_file = os.path.join(expected_dir, f"Suspect_Account_Letter_{account_number}.docx")
            
            if os.path.exists(expected_dir):
                print(f"SUCCESS: Folder 'suspect letter' exists at {expected_dir}")
                if os.path.exists(expected_file):
                    print(f"SUCCESS: File exists at {expected_file}")
                else:
                    print(f"FAILURE: File not found at {expected_file}")
            else:
                print(f"FAILURE: Folder 'suspect letter' not found at {expected_dir}")
                
                # Debug: what exists?
                parent = os.path.join(app.root_path, 'generated_letters', ack_no)
                if os.path.exists(parent):
                    print(f"Parent folder {ack_no} exists. Contents: {os.listdir(parent)}")
                else:
                    print(f"Parent folder {ack_no} does not exist.")
                    
        else:
            print(f"Request failed with {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Test Exception: {e}")

    # Test Victim Letter too
    account_number_v = "1111111111"
    payload_v = payload.copy()
    payload_v['letter_type'] = 'victim'
    payload_v['is_poh'] = False
    payload_v['account_number'] = account_number_v
    
    print(f"\nSending request for Victim Letter ACK: {ack_no}")
    try:
        res = client.post('/generate_letter_docx', json=payload_v, follow_redirects=True)
        
        if res.status_code == 200:
            expected_dir = os.path.join(app.root_path, 'generated_letters', ack_no, 'victim letter')
            expected_file = os.path.join(expected_dir, f"victim_Letter_{account_number_v}.docx")
            
            if os.path.exists(expected_dir):
                 print(f"SUCCESS: Folder 'victim letter' exists at {expected_dir}")
                 if os.path.exists(expected_file):
                    print(f"SUCCESS: File exists at {expected_file}")
            else:
                 print(f"FAILURE: Folder 'victim letter' not found.")
    except Exception as e:
        print(f"Test Exception Victim: {e}")

if __name__ == "__main__":
    test_suspect_letter_folder()
