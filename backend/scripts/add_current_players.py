import os
import sys
import pandas as pd

# Adjust path to import from app
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app import create_app, db
from app.models import Player, Team

def add_players_from_excel(file_path):
    """
    Read players from Excel file and add to database.
    
    Args:
        file_path (str): Path to the Excel file containing player stats
    """
    # Create Flask app context to interact with database
    app = create_app()
    with app.app_context():
        # Read Excel file, skipping the first row which contains headers
        df = pd.read_excel(file_path, header=1)
        
        # Print columns to debug
        print("Columns in DataFrame:", list(df.columns))
        
        # Ensure columns exist (adjust column names as needed)
        if 'Rk' not in df.columns or len(df.columns) < 2:
            print("Error: Unable to find player data columns.")
            return
        
        # Track added and skipped players
        added_players = 0
        skipped_players = 0
        
        # Iterate through rows
        for _, row in df.iterrows():
            # Skip header or empty rows
            if pd.isna(row[1]):  # Assuming player name is in the second column
                continue
            
            player_name = str(row[1]).strip()
            
            # Skip if player name is empty or looks like a header
            if not player_name or player_name in ['Player', 'Rk']:
                continue
            
            # Check if player already exists
            existing_player = Player.query.filter_by(full_name=player_name).first()
            if existing_player:
                print(f"Player {player_name} already exists. Skipping.")
                skipped_players += 1
                continue
            
            # Determine team (if possible)
            # Adjust column index for team as needed
            team = str(row[2]).strip() if len(row) > 2 else None
            
            # Create new player
            new_player = Player(full_name=player_name)
            
            # If team exists, try to link
            if team and team != 'TOT':
                existing_team = Team.query.filter(
                    (Team.name.ilike(f'%{team}%')) | 
                    (Team.abbreviation.ilike(team))
                ).first()
                
                if existing_team:
                    new_player.team_id = existing_team.id
                    print(f"Linked {player_name} to team {existing_team.name}")
                else:
                    print(f"Warning: Could not find team {team} for player {player_name}")
            
            # Add and commit
            db.session.add(new_player)
            added_players += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"Added {added_players} new players. Skipped {skipped_players} existing players.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing players to database: {e}")

def main():
    # Construct path to Excel file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    excel_path = os.path.join(base_dir, 'data', 'nba', 'NBA Player Stats 2024-25.xlsx')
    
    # Validate file exists
    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        sys.exit(1)
    
    # Add players
    add_players_from_excel(excel_path)

if __name__ == '__main__':
    main() 