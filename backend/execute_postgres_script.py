"""Execute PostgreSQL Script

This utility runs a PostgreSQL script directly against the database
using the same connection settings as the Flask application.
"""

import os
import sys
from app import create_app, db
from sqlalchemy import text

def execute_sql_file(filepath):
    """Execute a SQL script file against the database"""
    app = create_app()
    
    with open(filepath, 'r') as file:
        sql_script = file.read()
    
    with app.app_context():
        # Drop the token table if it exists to ensure clean creation
        try:
            db.session.execute(text("DROP TABLE IF EXISTS token CASCADE;"))
            db.session.commit()
            print("Dropped existing token table")
        except Exception as e:
            db.session.rollback()
            print(f"Error dropping token table: {e}")
        
        # Execute the main SQL script
        try:
            db.session.execute(text(sql_script))
            db.session.commit()
            print(f"Successfully executed SQL script: {filepath}")
            
            # Verify token table exists
            result = db.session.execute(text("SELECT to_regclass('public.token');")).scalar()
            if result:
                print("✅ Token table successfully created")
            else:
                print("❌ Token table was not created")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error executing SQL script: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python execute_postgres_script.py <sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    if not os.path.exists(sql_file):
        print(f"Error: File {sql_file} does not exist")
        sys.exit(1)
    
    execute_sql_file(sql_file)
