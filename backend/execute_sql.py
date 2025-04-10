from app import create_app, db
from sqlalchemy import text

def execute_sql_updates():
    app = create_app()
    with app.app_context():
        # Update Lakers to Los Angeles Lakers
        db.session.execute(text("UPDATE card SET team = 'Los Angeles Lakers' WHERE team = 'Lakers'"))
        
        # Update Grizzlies to Memphis Grizzlies
        db.session.execute(text("UPDATE card SET team = 'Memphis Grizzlies' WHERE team = 'Grizzlies'"))
        
        # Remove non-team values
        db.session.execute(text("UPDATE card SET team = NULL WHERE team IN ('Prizm', 'Shipping')"))
        
        # Commit the changes
        db.session.commit()
        print("SQL updates executed successfully")
        
        # Verify the changes
        teams = db.session.execute(text("SELECT DISTINCT team FROM card WHERE team IS NOT NULL")).fetchall()
        print("\nTeams in database after updates:")
        for team in sorted(teams):
            count = db.session.execute(text(f"SELECT COUNT(*) FROM card WHERE team = '{team[0]}'")).scalar()
            print(f"- {team[0]} ({count} cards)")

if __name__ == "__main__":
    execute_sql_updates() 