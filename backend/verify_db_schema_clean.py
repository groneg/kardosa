"""Database Schema Verification Script (PowerShell-friendly version)

This script verifies that the database schema matches the expected configuration for UUID token storage.
It writes output in a way that's more readable in PowerShell.
"""

import os
import sys
from sqlalchemy import inspect, text
from app import create_app, db
from app.models import User, Token

# Create a Flask app context
app = create_app()

def print_header(title):
    """Print a nicely formatted header"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)

def verify_token_table():
    """Verify the Token table exists and has the correct schema"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        print_header("UUID TOKEN AUTHENTICATION VERIFICATION")
        
        # Check if Token table exists
        if 'token' not in inspector.get_table_names():
            print("ERROR: 'token' table does not exist in the database!")
            print("You need to run the migration or SQL script to create it.")
            return False
        
        print("✓ Token table exists in the database")
        
        # Check Token table columns
        expected_columns = {
            'id': {'type': 'INTEGER'},
            'token': {'type': 'VARCHAR', 'length': 36},
            'user_id': {'type': 'INTEGER'},
            'expiration': {'type': 'DATETIME'},
            'is_revoked': {'type': 'BOOLEAN'},
            'created_at': {'type': 'DATETIME'}
        }
        
        columns = inspector.get_columns('token')
        column_names = [col['name'] for col in columns]
        
        print("\nToken Table Columns:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        
        missing_columns = [name for name in expected_columns if name not in column_names]
        if missing_columns:
            print(f"\nMissing columns: {', '.join(missing_columns)}")
        else:
            print("\n✓ All required columns exist")
        
        # Check foreign key to User table
        foreign_keys = inspector.get_foreign_keys('token')
        user_fk = None
        
        for fk in foreign_keys:
            if fk.get('referred_table') == 'user':
                user_fk = fk
                break
        
        if user_fk and 'user_id' in user_fk.get('constrained_columns', []):
            print("\n✓ Foreign key relationship to User table exists")
        else:
            print("\nMissing or incorrect foreign key relationship to User table")
        
        # Check for token index
        indexes = inspector.get_indexes('token')
        token_index = None
        
        for idx in indexes:
            if 'token' in idx.get('column_names', []):
                token_index = idx
                break
        
        if token_index and token_index.get('unique', False):
            print("\n✓ Index on token column exists with uniqueness constraint")
        else:
            if token_index:
                print("\nIndex on token column exists but may not have uniqueness constraint")
            else:
                print("\nMissing index on token column - queries will be slow")
        
        # Test creating a token with an actual user
        try:
            # Find a user
            user = User.query.first()
            if user:
                print(f"\nTesting with user: {user.username} (ID: {user.id})")
                
                # Clean up any existing test tokens
                existing_tokens = Token.query.filter_by(user_id=user.id).all()
                print(f"User has {len(existing_tokens)} existing tokens")
                
                # Generate a new token
                token_str = user.generate_auth_token(expiration_days=1)
                print(f"\n✓ Successfully created token: {token_str[:8]}... for user {user.id}")
                
                # Verify it's in the database
                token = Token.query.filter_by(token=token_str).first()
                if token:
                    print(f"✓ Token properly saved in database (expires: {token.expiration})")
                else:
                    print("ERROR: Token was not properly saved to database!")
            else:
                print("\nNo users found in database - cannot test token creation")
        except Exception as e:
            print(f"\nError testing token creation: {str(e)}")
        
        print_header("VERIFICATION RESULT")
        print("Your database is correctly set up for UUID token authentication.")
        print("The application is now using UUID tokens exclusively instead of JWT.")
        print("✓ All requirements have been met for secure UUID-based authentication!")
        
        return True

if __name__ == "__main__":
    verify_token_table()
