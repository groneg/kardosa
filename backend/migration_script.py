import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL database
conn = psycopg2.connect('postgresql://dosai:dosaidog@localhost:5432/kardosa')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cur = conn.cursor()

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

# Close the connection
cur.close()
conn.close()
print("Migration completed")
