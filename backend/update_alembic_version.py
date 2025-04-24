import psycopg2

conn = psycopg2.connect(
    dbname="kardosa",
    user="dosai",
    password="dosaidog",
    host="localhost"
)
cur = conn.cursor()
cur.execute("UPDATE alembic_version SET version_num = 'c847a2a9d9b7';")
conn.commit()
cur.close()
conn.close()
print("Alembic version updated!")
