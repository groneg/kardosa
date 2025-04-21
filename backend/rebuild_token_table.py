"""Rebuild Token Table Script

This script drops and recreates the token table using SQLAlchemy to ensure
it perfectly matches the model definition and resolves the login error.
"""

from app import create_app, db
from app.models import Token
from sqlalchemy import text

def rebuild_token_table():
    """Drop and recreate the token table using SQLAlchemy"""
    app = create_app()
    
    with app.app_context():
        # Use raw SQL to drop the table if it exists
        print("Dropping token table if it exists...")
        db.session.execute(text("DROP TABLE IF EXISTS token"))
        db.session.commit()
        
        # Create Token table using SQLAlchemy metadata
        print("Creating token table from SQLAlchemy model...")
        # Method 1: Create just the token table
        Token.__table__.create(db.engine)
        
        # Verify the table exists
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='token'"))
        tables = result.fetchall()
        
        if tables:
            print("✓ Token table successfully created!")
            
            # Check table structure
            result = db.session.execute(text("PRAGMA table_info(token)"))
            columns = result.fetchall()
            print("\nToken table columns:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        else:
            print("✗ Failed to create token table")
            
        print("\nRebuild complete. Now restart the application.")

if __name__ == "__main__":
    rebuild_token_table()
