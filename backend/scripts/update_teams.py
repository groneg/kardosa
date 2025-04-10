import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Card

# List of all NBA teams since 1980 (including current and former teams)
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
    "San Diego Rockets",  # Relocated to Houston in 1971 (included for completeness)
    "Buffalo Braves",     # Relocated to San Diego in 1978 (included for completeness)
]

def update_teams():
    app = create_app()
    with app.app_context():
        # Get all unique teams currently in the database
        existing_teams = db.session.query(Card.team).distinct().all()
        existing_teams = [team[0] for team in existing_teams if team[0] is not None]
        
        print(f"Found {len(existing_teams)} existing teams in the database")
        
        # Update all cards with standardized team names
        for team in existing_teams:
            # Find the closest match in our NBA_TEAMS list
            closest_match = None
            for nba_team in NBA_TEAMS:
                # Simple matching - could be improved with fuzzy matching
                if team.lower() in nba_team.lower() or nba_team.lower() in team.lower():
                    closest_match = nba_team
                    break
            
            if closest_match and closest_match != team:
                print(f"Updating '{team}' to '{closest_match}'")
                # Update all cards with this team name
                Card.query.filter_by(team=team).update({Card.team: closest_match})
        
        # Commit the changes
        db.session.commit()
        print("Team updates completed successfully")

if __name__ == "__main__":
    update_teams() 