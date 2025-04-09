# backend/scripts/load_reference_data.py
import os
import csv
import sys

# Adjust the path to include the 'backend' directory for sibling imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir) # Add backend dir to start of path

# Now imports should work as if run from 'backend' directory
from app import create_app, db
from app.models import Player, Team

# --- Configuration ---
# Assumes the CSV files from the dataset are in this directory
# Get project root based on new backend_dir definition
project_root = os.path.abspath(os.path.join(backend_dir, '..'))
DATA_DIR = os.path.join(backend_dir, 'data', 'nba')
# Specify the relevant CSV files (adjust filenames as needed)
BOX_SCORE_FILES = [
    'regular_season_box_scores_2010_2024_part_1.csv',
    'regular_season_box_scores_2010_2024_part_2.csv',
    'regular_season_box_scores_2010_2024_part_3.csv',
    'play_off_box_scores_2010_2024.csv'
]
TOTALS_FILES = [
    'regular_season_totals_2010_2024.csv',
    'play_off_totals_2010_2024.csv'
]
# --- End Configuration ---

def load_players():
    """Loads unique players from box score files."""
    print("Loading players...")
    players_added = 0
    players_skipped = 0
    unique_player_names = set()

    # First pass: Collect all unique names to avoid DB checks in loop
    for filename in BOX_SCORE_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Box score file not found: {filepath}")
            continue
        print(f"Reading players from: {filename}")
        try:
            with open(filepath, mode='r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    # Assuming 'personName' column exists and is correct
                    if 'personName' in row and row['personName']:
                        unique_player_names.add(row['personName'].strip())
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    # Second pass: Add unique names to DB
    print(f"Found {len(unique_player_names)} unique player names. Adding to DB...")
    existing_players = {p.full_name for p in Player.query.all()}

    for name in unique_player_names:
        if name not in existing_players:
            player = Player(full_name=name)
            db.session.add(player)
            players_added += 1
        else:
            players_skipped += 1

    db.session.commit()
    print(f"Finished loading players. Added: {players_added}, Skipped (already exist): {players_skipped}")

def load_teams():
    """Loads unique teams from totals files."""
    print("Loading teams...")
    teams_added = 0
    teams_skipped = 0
    unique_teams = set() # Store tuples of (name, abbr)

    # First pass: Collect unique teams
    for filename in TOTALS_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Totals file not found: {filepath}")
            continue
        print(f"Reading teams from: {filename}")
        try:
            with open(filepath, mode='r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    # Assuming 'TEAM_NAME' and 'TEAM_ABBREVIATION' columns exist
                    if row.get('TEAM_NAME') and row.get('TEAM_ABBREVIATION'):
                        name = row['TEAM_NAME'].strip()
                        abbr = row['TEAM_ABBREVIATION'].strip()
                        unique_teams.add((name, abbr))
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    # Second pass: Add unique teams to DB
    print(f"Found {len(unique_teams)} unique team entries. Adding to DB...")
    # Query existing teams once
    existing_teams = {t.abbreviation: t.name for t in Team.query.all()}

    for name, abbr in unique_teams:
        # Skip if abbreviation already exists
        if abbr not in existing_teams:
            # Check if the name exists with a *different* abbreviation (unlikely but possible)
            if any(existing_name == name for existing_name in existing_teams.values()):
                print(f"Warning: Team name '{name}' already exists with a different abbreviation. Skipping ({abbr}).")
                teams_skipped += 1
                continue

            team = Team(name=name, abbreviation=abbr)
            db.session.add(team)
            teams_added += 1
            existing_teams[abbr] = name # Add to our in-memory check set
        else:
            # Check if the existing team has a different name
            if existing_teams[abbr] != name:
                print(f"Warning: Abbreviation '{abbr}' already exists for team '{existing_teams[abbr]}'. Skipping new entry '{name}'.")
            teams_skipped += 1 # Skipped due to existing abbreviation

    db.session.commit()
    print(f"Finished loading teams. Added: {teams_added}, Skipped (already exist/conflict): {teams_skipped}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        load_players()
        print("-"*20)
        load_teams()
        print("Reference data loading complete.") 