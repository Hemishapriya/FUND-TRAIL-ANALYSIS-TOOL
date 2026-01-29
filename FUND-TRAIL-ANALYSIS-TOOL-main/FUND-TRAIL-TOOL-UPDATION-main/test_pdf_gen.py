import unittest
from app import app, db, User
import json
import io

class TestPDFGen(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app = app.test_client()
        
        # We assume the DB is already set up and has the admin user
        # from app.py: admin / admin123

    def login(self):
        return self.app.post('/login', data=dict(
            username='admin',
            password='admin123',
            role='Admin'
        ), follow_redirects=True)

    def test_download_fundtrail_pdf(self):
        self.login()
        
        # Mock data similar to what frontend sends
        payload = {
            "ack_no": "TEST-ACK-123",
            "nodes": [
                {
                    "layer": "1",
                    "account_number": "1234567890",
                    "bank": "Test Bank",
                    "branch": "Main Branch",
                    "ifsc": "TEST0001234",
                    "txn_id": "TXN001",
                    "amount": "50000",
                    "disputed_amount": "50000",
                    "hold_amount": None
                },
                {
                    "layer": "2",
                    "account_number": "0987654321",
                    "bank": "Suspect Bank",
                    "branch": "City Branch",
                    "ifsc": "SUSP0005678",
                    "txn_id": "TXN002",
                    "amount": "20000",
                    "disputed_amount": "20000",
                    "hold_amount": "20000"
                }
            ]
        }
        
        response = self.app.post('/download_fundtrail_pdf', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertTrue(response.data.startswith(b'%PDF'), "Response is not a PDF file")
        
        # Optionally save it to verify visually if needed (locally)
        # with open("test_output.pdf", "wb") as f:
        #     f.write(response.data)
        print("PDF generated successfully")

if __name__ == '__main__':
    unittest.main()
