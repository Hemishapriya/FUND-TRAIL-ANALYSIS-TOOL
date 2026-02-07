
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='officer').first()
    if user:
        print(f"User 'officer' found. Current role: {user.role}")
        
        # Reset password to 'officer123' (bypassing complexity check)
        user.password_hash = generate_password_hash('officer123')
        print("Password reset to 'officer123'.")
        
        # Reset lock status
        user.failed_login_attempts = 0
        user.account_locked_until = None
        print("Account lock status reset.")
        
        db.session.commit()
        print("Changes committed to database.")
    else:
        print("User 'officer' not found. Creating it...")
        # Create user if not exists
        user = User(username='officer', role='Investigative Officer')
        user.password_hash = generate_password_hash('officer123')
        db.session.add(user)
        db.session.commit()
        print("User 'officer' created with password 'officer123'.")
