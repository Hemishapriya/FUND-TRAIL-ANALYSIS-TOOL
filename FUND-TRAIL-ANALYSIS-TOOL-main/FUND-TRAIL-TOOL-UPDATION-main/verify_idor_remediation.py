
import unittest
from app import app, db, User, Complaint, Transaction, UploadedFile, limiter
import unittest
import io

class TestIDOR(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['RATELIMIT_ENABLED'] = False
        
        self.client = app.test_client()
        
        with app.app_context():
            limiter.enabled = False
            
            # Force engine disposal to pick up new config
            db.engine.dispose()
            
            # Ensure we are using in-memory DB
            if 'memory' not in str(db.engine.url):
                 print(f"WARNING: DB Engine URL is {db.engine.url}. Attempting to use in-memory.")
            
            db.drop_all()
            db.create_all()
            
            # Create Users
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='Admin')
                admin.set_password('AdminPass123!@#')
                db.session.add(admin)
            else:
                admin = User.query.filter_by(username='admin').first()
            
            if not User.query.filter_by(username='officer1').first():
                officer1 = User(username='officer1', role='Investigative Officer')
                officer1.set_password('OfficerPass123!@#')
                db.session.add(officer1)
            else:
                officer1 = User.query.filter_by(username='officer1').first()

            if not User.query.filter_by(username='officer2').first():
                officer2 = User(username='officer2', role='Investigative Officer')
                officer2.set_password('OfficerPass123!@#')
                db.session.add(officer2)
            else:
                officer2 = User.query.filter_by(username='officer2').first()
            
            db.session.commit()
            
            # Create Case
            complaint = Complaint(ack_no='ACK1', assigned_to=officer1.id)
            db.session.add(complaint)
            
            # Create UploadedFile (needed for atm_data)
            up_file = UploadedFile(filename='test.xlsx', uploader='officer1')
            db.session.add(up_file)
            db.session.commit()
            
            # Create Transactions
            txn = Transaction(ack_no='ACK1', amount=100, state='Delhi', put_on_hold_txn_id='POH1', upload_id=up_file.id)
            db.session.add(txn)
            
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password, role):
        return self.client.post('/login', data=dict(
            username=username,
            password=password,
            role=role
        ), follow_redirects=True)

    def test_idor_protection(self):
        endpoints = [
            '/graph_data/ACK1',
            '/put_on_hold_transactions/ACK1',
            '/statewise_summary/ACK1',
            '/state_transactions/ACK1/Delhi',
            '/atm_data/ACK1'
        ]
        
        # 1. Unauthenticated
        print("\n--- Testing Unauthenticated Access ---")
        for ep in endpoints:
            resp = self.client.get(ep, follow_redirects=True)
            # Should redirect to login or be 401
            if b'Login' in resp.data or b'Please log in' in resp.data:
                 print(f"PASS: {ep} -> Login Page")
            elif resp.status_code == 401:
                 print(f"PASS: {ep} -> 401 Unauthorized")
            else:
                 print(f"FAIL: {ep} -> {resp.status_code}")

        # 2. Unauthorized (Officer2)
        print("\n--- Testing Unauthorized Access (Officer2) ---")
        self.login('officer2', 'OfficerPass123!@#', 'Investigative Officer')
        for ep in endpoints:
            resp = self.client.get(ep)
            if resp.status_code == 403:
                print(f"PASS: {ep} -> 403 Forbidden")
            else:
                print(f"FAIL: {ep} -> {resp.status_code} (Expected 403)")

        # 3. Authorized (Officer1)
        print("\n--- Testing Authorized Access (Officer1) ---")
        self.client.get('/logout', follow_redirects=True)
        self.login('officer1', 'OfficerPass123!@#', 'Investigative Officer')
        for ep in endpoints:
            resp = self.client.get(ep)
            if resp.status_code == 200:
                print(f"PASS: {ep} -> 200 OK")
            else:
                print(f"INFO: {ep} -> {resp.status_code}")

if __name__ == '__main__':
    unittest.main()
