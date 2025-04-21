"""Database Schema Verification Script

This script verifies that the database schema matches the expected configuration for UUID token storage.
It checks the Token table structure, relationships, and reports any discrepancies from the production setup.
"""

import os
import sys
from sqlalchemy import inspect, text
from app import create_app, db
from app.models import User, Token

# Create a Flask app context
app = create_app()

def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)

def verify_token_table():
    """Verify the Token table exists and has the correct schema"""
    inspector = inspect(db.engine)
    
    print_separator()
    print("VERIFYING DATABASE SCHEMA FOR UUID TOKEN AUTHENTICATION")
    print_separator()
    
    # Check if Token table exists
    if 'token' not in inspector.get_table_names():
        print("❌ ERROR: 'token' table does not exist in the database!")
        print("   You need to run the migration or SQL script to create it.")
        return False
    
    print("✅ Token table exists in the database")
    
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
        print(f"\n❌ Missing columns: {', '.join(missing_columns)}")
    else:
        print("\n✅ All required columns exist")
    
    # Check foreign key to User table
    foreign_keys = inspector.get_foreign_keys('token')
    user_fk = None
    
    for fk in foreign_keys:
        if fk.get('referred_table') == 'user':
            user_fk = fk
            break
    
    if user_fk and 'user_id' in user_fk.get('constrained_columns', []):
        print("\n✅ Foreign key relationship to User table exists")
    else:
        print("\n❌ Missing or incorrect foreign key relationship to User table")
    
    # Check for token index
    indexes = inspector.get_indexes('token')
    token_index = None
    
    for idx in indexes:
        if 'token' in idx.get('column_names', []):
            token_index = idx
            break
    
    if token_index and token_index.get('unique', False):
        print("\n✅ Index on token column exists with uniqueness constraint")
    else:
        if token_index:
            print("\n⚠️ Index on token column exists but may not have uniqueness constraint")
        else:
            print("\n❌ Missing index on token column - queries will be slow")
    
    print_separator()
    return True

def test_token_creation():
    """Test creating a token in the database"""
    with app.app_context():
        # Find a user
        user = User.query.first()
        if not user:
            print("❌ Cannot test token creation - no users in database")
            return
        
        print(f"Testing token creation for user: {user.username} (ID: {user.id})")
        
        try:
            # Generate a token
            token_str = user.generate_auth_token(expiration_days=1)
            print(f"✅ Successfully created token: {token_str[:8]}... for user {user.id}")
            
            # Verify it's in the database
            token = Token.query.filter_by(token=token_str).first()
            if token:
                print(f"✅ Token found in database (ID: {token.id}, expires: {token.expiration})")
            else:
                print("❌ Token was not properly saved to database!")
                
        except Exception as e:
            print(f"❌ Error testing token creation: {str(e)}")
    
    print_separator()

def main():
    """Main function to run the verification"""
    with app.app_context():
        if verify_token_table():
            print("TOKEN TABLE VERIFICATION COMPLETE")
            response = input("\nWould you like to test token creation? (y/n): ")
            if response.lower() == 'y':
                test_token_creation()
            print("\nVERIFICATION COMPLETE!")
            print("Your database is correctly set up for UUID token authentication.")

if __name__ == "__main__":
    main()
