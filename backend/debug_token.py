"""Debug Token model with PostgreSQL

This script tests creating a token directly in PostgreSQL to identify any issues.
"""

import sys
import traceback
from datetime import datetime, timedelta
import uuid
from app import create_app, db
from app.models import User, Token

app = create_app()

def debug_token_creation():
    """Debug token creation with verbose error handling"""
    with app.app_context():
        try:
            # Find a user to work with
            user = User.query.first()
            if not user:
                print("No users found in database")
                return
                
            print(f"Testing with user: {user.username} (ID: {user.id})")
            
            # Generate UUID
            token_uuid = str(uuid.uuid4())
            print(f"Generated UUID: {token_uuid}")
            
            # Create expiration timestamp (PostgreSQL format)
            expiration = datetime.utcnow() + timedelta(days=1)
            print(f"Expiration: {expiration} (type: {type(expiration)})")
            
            # Create token object
            print("Creating token object...")
            token = Token(
                token=token_uuid,
                user_id=user.id,
                expiration=expiration,
                is_revoked=False,
                created_at=datetime.utcnow()
            )
            
            # Print token details before saving
            print(f"Token object: {token!r}")
            print(f"Token ID: {token.id}")
            print(f"Token string: {token.token}")
            print(f"User ID: {token.user_id}")
            print(f"Expiration: {token.expiration}")
            print(f"Is revoked: {token.is_revoked}")
            print(f"Created at: {token.created_at}")
            
            # Try to add and commit
            print("\nAdding token to session...")
            db.session.add(token)
            print("Committing session...")
            db.session.commit()
            print("Successfully saved token to database!")
            
            # Query to confirm it exists
            saved_token = Token.query.filter_by(token=token_uuid).first()
            if saved_token:
                print(f"\nConfirmed token in database: {saved_token!r}")
                print(f"Saved token ID: {saved_token.id}")
            else:
                print("\nWARNING: Token not found in database after save!")
                
        except Exception as e:
            db.session.rollback()
            print(f"\nERROR: {type(e).__name__}: {str(e)}")
            print("\nDetailed traceback:")
            traceback.print_exc()
            
            # Check if the token table exists
            print("\nVerifying token table existence...")
            try:
                result = db.session.execute(db.text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='token');")).scalar()
                print(f"Token table exists: {result}")
                
                if result:
                    # Check columns
                    columns = db.session.execute(db.text("SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name='token';")).fetchall()
                    print("\nToken table columns:")
                    for column in columns:
                        print(f"  - {column[0]}: {column[1]}" + (f" (length: {column[2]})" if column[2] else ""))
            except Exception as table_check_error:
                print(f"Error checking table: {table_check_error}")

if __name__ == "__main__":
    debug_token_creation()
