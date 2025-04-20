import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration(database_url=None):
    """Run database migration to update card_year column to string type.
    
    Args:
        database_url: Production database URL from environment or explicit parameter
    """
    if not database_url:
        # Try to get from environment
        database_url = os.environ.get('DATABASE_URL')
        
    if not database_url:
        print("ERROR: No database URL provided. Please set DATABASE_URL environment variable or provide as parameter.")
        sys.exit(1)
        
    print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'HIDDEN'}")
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check if any data exists in the card table
        cur.execute("SELECT COUNT(*) FROM card")
        card_count = cur.fetchone()[0]
        print(f"Found {card_count} existing cards in database")
        
        # Back up existing card data if any exists
        if card_count > 0:
            print("Backing up existing card data...")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS card_backup AS 
            SELECT * FROM card;
            """)
            print("Backup completed successfully")
        
        # Alter the card_year column type to character varying
        print("Altering card_year column type from integer to character varying...")
        try:
            # First, convert all existing integer values to strings
            cur.execute("""
            ALTER TABLE card
            ALTER COLUMN card_year TYPE varchar(20) USING card_year::varchar;
            """)
            print("Successfully altered card_year column type")
        except Exception as e:
            print(f"Error altering column: {e}")
            if card_count > 0:
                print("WARNING: Column alteration failed, but you have a backup in card_backup table")
            else:
                print("No existing data was affected")
        
        # Close the connection
        cur.close()
        conn.close()
        print("Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Database migration failed: {e}")
        return False

if __name__ == "__main__":
    # Can be run directly with database URL as argument
    database_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_migration(database_url)
