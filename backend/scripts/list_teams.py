import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Card

def list_teams():
    app = create_app()
    with app.app_context():
        # Get all unique teams currently in the database
        existing_teams = db.session.query(Card.team).distinct().all()
        existing_teams = [team[0] for team in existing_teams if team[0] is not None]
        
        print(f"Found {len(existing_teams)} teams in the database:")
        for team in sorted(existing_teams):
            # Count how many cards have this team
            count = Card.query.filter_by(team=team).count()
            print(f"- {team} ({count} cards)")

if __name__ == "__main__":
    list_teams() 