import re
from thefuzz import process as fuzzy_process # Corrected import
from .models import Player, Team, Card
from . import db
from .cache import persistent_cache
from datetime import datetime

# Simple regex patterns (can be improved)
YEAR_PATTERN = re.compile(r'\b(19[5-9]\d|20[0-4]\d)(?:-?(?:19[5-9]\d|20[0-4]\d|\d{2}))?\b') # Matches 1950-2049, with optional second year
NUMBER_PATTERN = re.compile(r'#([A-Za-z0-9]+)\b')

# --- Pre-load reference data for efficiency ---
# Load once when the module is imported (or use caching)
# Ensure this runs within an app context if needed immediately, or load lazily
_PLAYER_NAMES = []
_TEAM_MAP = {}

# Common basketball card manufacturers
COMMON_MANUFACTURERS = [
    "Topps",
    "Panini",
    "Upper Deck",
    "Fleer",
    "Donruss",
    "Hoops",
    "SkyBox",
    "Score",
    "Classic",
    "Press Pass"
]

def load_reference_data_cache():
    """Loads player names and team map into memory. Requires app context."""
    global _PLAYER_NAMES, _TEAM_MAP
    
    # Try to get from Redis cache first
    cached_players = persistent_cache.get_cached_players()
    cached_teams = persistent_cache.get_cached_teams()
    
    if cached_players:
        _PLAYER_NAMES = [player_data['full_name'] for player_data in cached_players.values()]
        print(f"Loaded {len(_PLAYER_NAMES)} player names from cache")
    else:
        # Fallback to database if cache is empty
        players = Player.query.all()
        _PLAYER_NAMES = [p.full_name for p in players]
        print(f"Loaded {len(_PLAYER_NAMES)} player names from database")
        # Cache for future use
        persistent_cache.cache_players()
    
    if cached_teams:
        _TEAM_MAP = {
            team_data['abbreviation']: team_data['name'] 
            for team_data in cached_teams.values()
        }
        # Add lowercase name lookups
        for team_data in cached_teams.values():
            _TEAM_MAP[team_data['name'].lower()] = team_data['name']
        print(f"Loaded {len(_TEAM_MAP)} team entries from cache")
    else:
        # Fallback to database if cache is empty
        _TEAM_MAP = {t.abbreviation: t.name for t in Team.query.all()}
        for t in Team.query.all():
             _TEAM_MAP[t.name.lower()] = t.name
        print(f"Loaded {len(_TEAM_MAP)} team entries from database")
        # Cache for future use
        persistent_cache.cache_teams()

def normalize_player_name(extracted_name, min_score=85):
    """Finds the best match for the extracted player name in the DB using fuzzy matching.

    Args:
        extracted_name (str): The name potentially extracted from eBay title.
        min_score (int): The minimum score (0-100) required to accept a match.

    Returns:
        str: The normalized name from the DB, or None if no good match found.
    """
    if not _PLAYER_NAMES:
        print("Warning: Player name cache is empty. Call load_reference_data_cache() first.")
        # Attempt direct match as fallback
        player = Player.query.filter(Player.full_name.ilike(extracted_name)).first()
        return player.full_name if player else None

    # Use fuzzy matching to find the best match above the threshold
    match, score = fuzzy_process.extractOne(extracted_name, _PLAYER_NAMES)

    if score >= min_score:
        print(f"Fuzzy matched '{extracted_name}' to '{match}' with score {score}")
        return match
    else:
        print(f"Warning: No good fuzzy match found for player '{extracted_name}' (Best: '{match}', Score: {score} < {min_score}).")
        return None # Indicate no confident match found

def normalize_team_name(extracted_name):
    """Finds a matching team name from the cached map."
    """
    if not _TEAM_MAP:
         print("Warning: Team map cache is empty. Call load_reference_data_cache() first.")
         # Attempt direct DB query as fallback
         team = Team.query.filter(
             (Team.abbreviation.ilike(extracted_name)) |
             (Team.name.ilike(f'%{extracted_name}%'))
         ).first()
         return team.name if team else extracted_name # Return original if no fallback match

    # Check abbreviation first, then lowercase name
    normalized_name = _TEAM_MAP.get(extracted_name)
    if normalized_name:
        return normalized_name
    normalized_name = _TEAM_MAP.get(extracted_name.lower())
    if normalized_name:
        return normalized_name

    print(f"Warning: Team '{extracted_name}' not found in reference map.")
    return extracted_name # Return original if not found

def normalize_season_year(year_str):
    """
    Convert various year formats to a season format YYYY-YY.
    
    Args:
        year_str (str): The year string from input.
    
    Returns:
        str: Formatted season string in YYYY-YY format.
    
    Examples:
        "2024" -> "2023-24"
        "2022" -> "2021-22"
        "24" -> "2023-24"
        "22" -> "2021-22"
        "2023-24" -> "2023-24"
        "23-24" -> "2023-24"
    """
    # Remove any non-numeric characters except hyphen
    year_str = re.sub(r'[^\d-]', '', year_str)
    
    # Split on hyphen if present
    parts = year_str.split('-')
    
    if len(parts) == 2:
        # Full season format (e.g., "2023-24" or "23-24")
        first_year = parts[0]
        second_year = parts[1]
        
        # Handle two-digit years
        if len(first_year) == 2:
            first_year = '20' + first_year
        if len(second_year) == 2:
            second_year = '20' + second_year
            
        # Validate the years make sense
        first_year_int = int(first_year)
        second_year_int = int(second_year)
        
        if second_year_int != first_year_int + 1:
            # If years don't make sense, assume first year is correct
            second_year_int = first_year_int + 1
            second_year = str(second_year_int)
            
        return f"{first_year}-{second_year[-2:]}"
    else:
        # Single year format
        year = parts[0]
        
        # Handle two-digit year
        if len(year) == 2:
            year = '20' + year
            
        year_int = int(year)
        
        # Assume the input year is the second year of the season
        first_year = year_int - 1
        return f"{first_year}-{str(year_int)[-2:]}"

def format_season_year(year_int):
    """
    Convert an integer year to a YYYY-YY format string.
    
    Args:
        year_int (int or str): The year as an integer or string.
    
    Returns:
        str: Formatted season string in YYYY-YY format.
    
    Examples:
        2024 -> "2023-24"
        2022 -> "2021-22"
        "2024" -> "2023-24"
    """
    if year_int is None:
        return None
    # Convert to int if it's a string
    year_int = int(year_int) if isinstance(year_int, str) else year_int
    return f"{year_int-1}-{str(year_int)[-2:]}"

def parse_season_year(year_str):
    """
    Convert a YYYY-YY format string to an integer year.
    
    Args:
        year_str (str): The year string in YYYY-YY format.
    
    Returns:
        int: The year as an integer.
    
    Examples:
        "2023-24" -> 2024
        "2021-22" -> 2022
    """
    if not year_str or '-' not in year_str:
        return None
    
    parts = year_str.split('-')
    if len(parts) != 2:
        return None
    
    try:
        # Take the second year (e.g., "2023-24" -> 2024)
        second_year = parts[1]
        if len(second_year) == 2:
            first_year_prefix = parts[0][:2]
            second_year = first_year_prefix + second_year
        return int(second_year)
    except ValueError:
        return None

def normalize_manufacturer(extracted_name, min_score=85):
    """Finds the best match for the extracted manufacturer name using fuzzy matching.

    Args:
        extracted_name (str): The manufacturer name potentially extracted from eBay title.
        min_score (int): The minimum score (0-100) required to accept a match.

    Returns:
        str: The normalized manufacturer name, or None if no good match found.
    """
    if not extracted_name:
        return None

    # Use fuzzy matching to find the best match above the threshold
    match, score = fuzzy_process.extractOne(extracted_name, COMMON_MANUFACTURERS)

    if score >= min_score:
        print(f"Fuzzy matched manufacturer '{extracted_name}' to '{match}' with score {score}")
        return match
    else:
        print(f"Warning: No good fuzzy match found for manufacturer '{extracted_name}' (Best: '{match}', Score: {score} < {min_score}).")
        return None

def map_ebay_result_to_card_data(ebay_result):
    """Parses the eBay API response (searchByImage) and maps to Card fields.

    Args:
        ebay_result (dict): The JSON response dictionary from the eBay API.

    Returns:
        dict: A dictionary containing mapped data suitable for creating a Card object,
              or None if no suitable item found or mapping fails.
    """
    if not ebay_result or 'itemSummaries' not in ebay_result or not ebay_result['itemSummaries']:
        print("No item summaries found in eBay result.")
        return None

    # --- Use the first result as the most likely match (simplistic approach) ---
    item = ebay_result['itemSummaries'][0]
    title = item.get('title', '')
    print(f"Mapping data from eBay item: {item.get('itemId')}, Title: {title}")

    mapped_data = {
        'player_name': None,
        'card_year': None,
        'manufacturer': None,
        'card_number': None,
        'team': None,
        'grade': None,
        'image_url': None
    }

    # --- Basic Parsing from Title (Needs significant improvement/heuristics) ---
    if title:
        # Extract Year
        year_match = YEAR_PATTERN.search(title)
        if year_match:
            try:
                # Get the full matched year string
                year_str = year_match.group(0)
                # Convert to season format
                season_year = normalize_season_year(year_str)
                # Store the season format directly
                mapped_data['card_year'] = season_year
                # Remove year from title for further parsing
                title = title.replace(year_match.group(0), '').strip()
                print(f"Extracted and normalized year: {year_str} -> {mapped_data['card_year']}")
            except ValueError as e:
                print(f"Error normalizing year '{year_str}': {e}")
                pass

        # Extract Card Number
        number_match = NUMBER_PATTERN.search(title)
        if number_match:
            mapped_data['card_number'] = number_match.group(1)
            title = title.replace(number_match.group(0), '').strip()

        # --- Extract and Normalize Player Name ---
        # Iterate through known player names from the cache
        found_player_name = None
        normalized_player = None
        if _PLAYER_NAMES: # Ensure cache is loaded
            # Sort player names by length in descending order to match longer names first
            # This helps avoid partial matches (e.g., "Jordan" in "Michael Jordan")
            sorted_player_names = sorted(_PLAYER_NAMES, key=len, reverse=True)
            for known_player_name in sorted_player_names:
                # Use regex word boundaries to avoid partial matches within words
                # Case-insensitive search to catch variations
                if re.search(r'\b' + re.escape(known_player_name) + r'\b', title, re.IGNORECASE):
                    normalized_player = known_player_name
                    found_player_name = known_player_name
                    print(f"Found player match: '{found_player_name}'")
                    # Optional: Remove the found player name from title for further parsing
                    # title = re.sub(r'\b' + re.escape(found_player_name) + r'\b', '', title, flags=re.IGNORECASE).strip()
                    break # Stop after finding the first (longest) match

        mapped_data['player_name'] = normalized_player # Store normalized name or None

        # Attempt to identify Team (often at the end)
        # This is also naive
        potential_team = title.split(' ')[-1]
        # Check if potential team is part of the player name to avoid self-match
        is_part_of_player_name = False
        if mapped_data['player_name'] and potential_team.lower() in mapped_data['player_name'].lower():
             is_part_of_player_name = True

        if not is_part_of_player_name:
             mapped_data['team'] = normalize_team_name(potential_team)
        else:
             mapped_data['team'] = None # Clear team if it matched player name part

        # Attempt to identify Manufacturer using fuzzy matching
        # Look for manufacturer names in the title
        for manufacturer in COMMON_MANUFACTURERS:
            if re.search(r'\b' + re.escape(manufacturer) + r'\b', title, re.IGNORECASE):
                mapped_data['manufacturer'] = manufacturer
                print(f"Found manufacturer match: '{manufacturer}'")
                break
        
        # If no direct match found, try fuzzy matching on the entire title
        if not mapped_data['manufacturer']:
            mapped_data['manufacturer'] = normalize_manufacturer(title)

    # --- Get Grade from Condition ---
    condition = item.get('condition')
    if condition:
        # Basic check, could refine (e.g., map "PSA 10" if found)
        if 'Graded' in condition or condition.startswith('PSA') or condition.startswith('BGS') or condition.startswith('SGC'):
             mapped_data['grade'] = condition # Store full condition string for now
        elif condition.lower() == 'ungraded' or condition.lower() == 'raw':
             mapped_data['grade'] = None # Explicitly set to None for ungraded
        else:
             mapped_data['grade'] = f"Condition: {condition}" # Store other conditions

    # Basic validation - Now requires a *normalized* player name
    if not mapped_data['player_name']:
        print("Failed to find a matching player name in database from eBay data.")
        return None
        
    print(f"Mapped Data: {mapped_data}")
    return mapped_data

def save_card_from_data(data, user_id):
    try:
        # Map the data to the correct fields
        mapped_data = {
            'player_name': data.get('player_name'),
            'card_year': data.get('card_year'),
            'manufacturer': data.get('manufacturer'),
            'card_number': data.get('card_number'),
            'team': data.get('team'),
            'grade': data.get('grade'),
            'image_url': data.get('image_url'),
            'notes': data.get('notes'),
            'sport': data.get('sport'),
            'owner_id': user_id,
            'date_added': datetime.utcnow()
        }

        # Detailed validation logging
        missing_required = []
        for field in ['player_name', 'card_year', 'manufacturer', 'owner_id']:
            if not mapped_data.get(field):
                missing_required.append(field)
        
        if missing_required:
            error_msg = f"Missing required fields: {', '.join(missing_required)}"
            print(f"ERROR: {error_msg}")
            return None

        print(f"Saving card with data: player={mapped_data['player_name']}, year={mapped_data['card_year']}, manufacturer={mapped_data['manufacturer']}, owner_id={mapped_data['owner_id']}")
        
        # Create new card
        new_card = Card(**mapped_data)
        db.session.add(new_card)
        db.session.commit()
        print(f"Successfully saved card ID: {new_card.id}")

        return new_card
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to save card: {str(e)}")
        raise Exception(f"Error saving card to database: {str(e)}")

# TODO: Add function to create/save Card object from mapped_data