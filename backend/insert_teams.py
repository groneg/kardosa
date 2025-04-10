from app import create_app, db
from app.models import Card
from sqlalchemy import text

# List of all NBA teams (current and former since 1980)
NBA_TEAMS = [
    # Current Teams
    "Atlanta Hawks",
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "Los Angeles Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards",
    
    # Former Teams (since 1980)
    "Charlotte Bobcats",  # Renamed to Hornets in 2014
    "New Jersey Nets",    # Renamed to Brooklyn Nets in 2012
    "Seattle SuperSonics", # Relocated to Oklahoma City in 2008
    "Vancouver Grizzlies", # Relocated to Memphis in 2001
    "Washington Bullets",  # Renamed to Wizards in 1997
    "New Orleans Hornets", # Renamed to Pelicans in 2013
    "New Orleans/Oklahoma City Hornets", # Temporary name during Katrina
    "San Diego Clippers", # Relocated to Los Angeles in 1984
    "Kansas City Kings",  # Relocated to Sacramento in 1985
    "San Diego Rockets",  # Relocated to Houston in 1971
    "Buffalo Braves",     # Relocated to San Diego in 1978
]

def insert_teams():
    app = create_app()
    with app.app_context():
        # Get current teams in database
        current_teams = db.session.execute(text("SELECT DISTINCT team FROM card WHERE team IS NOT NULL")).fetchall()
        current_teams = [team[0] for team in current_teams]
        
        print(f"Current teams in database: {len(current_teams)}")
        for team in sorted(current_teams):
            print(f"- {team}")
        
        # Create a temporary card for each team that doesn't exist
        for team in NBA_TEAMS:
            if team not in current_teams:
                # Create a temporary card with this team
                temp_card = Card(
                    player_name="Temporary",
                    team=team,
                    owner_id=1  # Assuming user ID 1 exists
                )
                db.session.add(temp_card)
                print(f"Adding team: {team}")
        
        # Commit the changes
        db.session.commit()
        
        # Verify the changes
        updated_teams = db.session.execute(text("SELECT DISTINCT team FROM card WHERE team IS NOT NULL")).fetchall()
        print(f"\nTeams in database after update: {len(updated_teams)}")
        for team in sorted(updated_teams):
            count = db.session.execute(text(f"SELECT COUNT(*) FROM card WHERE team = '{team[0]}'")).scalar()
            print(f"- {team[0]} ({count} cards)")

if __name__ == "__main__":
    insert_teams() 