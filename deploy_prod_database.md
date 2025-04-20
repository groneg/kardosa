# Deploying Database Changes to Production

## Instructions for Updating Production PostgreSQL Schema

We've made an important schema change locally (changing `card_year` from integer to string) that needs to be applied to your production database as well. Here's how to apply this change to your render.com hosted PostgreSQL database:

### Option 1: Using the Migration Script Directly on Render

1. Add the `prod_migration.py` script to your Git repository:
   ```
   git add backend/prod_migration.py
   git commit -m "Add production database migration script"
   git push origin main
   ```

2. Connect to your render.com dashboard and navigate to your backend service

3. Open a Shell to your backend service using the render.com dashboard

4. Run the migration script with your production DATABASE_URL:
   ```
   cd /opt/render/project/src/backend
   python prod_migration.py $DATABASE_URL
   ```

### Option 2: Run Migration Locally with Production Connection String

1. Get your PostgreSQL connection string from render.com dashboard (Settings > Environment > DATABASE_URL)

2. Run the migration script locally with the production connection string:
   ```
   cd backend
   python prod_migration.py "your_production_connection_string_here"
   ```

### Option 3: Run SQL Statement Directly

Alternatively, you can run the SQL statement directly on your database using the render.com PostgreSQL dashboard:

1. Log in to render.com and navigate to your database service

2. Click on "Connect" and then "Connect to Database"

3. In the SQL editor, run:
   ```sql
   -- Create backup first (recommended)
   CREATE TABLE IF NOT EXISTS card_backup AS SELECT * FROM card;
   
   -- Alter column type
   ALTER TABLE card ALTER COLUMN card_year TYPE varchar(20) USING card_year::varchar;
   ```

### Verify the Migration

After applying the change, verify that the schema has been updated by running:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'card' AND column_name = 'card_year';
```

You should see `varchar` as the data type instead of `integer`.

## Note on Data Safety

The migration script includes automatic backup functionality - it will create a `card_backup` table before making any changes. If anything goes wrong, you can restore your data from this backup table.
