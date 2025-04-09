import re
from .models import Player, Team, Card
from . import db

# Simple regex patterns (can be improved)
YEAR_PATTERN = re.compile(r'\b(19[5-9]\d|20[0-4]\d)\b') # Matches 1950-2049
NUMBER_PATTERN = re.compile(r'#([A-Za-z0-9]+)\b')

def normalize_player_name(extracted_name):
    """Attempts to find a matching player in the DB.
       Returns the normalized name or the original if no match.
    """
    # Simple exact match for now
    player = Player.query.filter(Player.full_name.ilike(extracted_name)).first()
    if player:
        return player.full_name
    # TODO: Add fuzzy matching or alias lookup later
    print(f"Warning: Player '{extracted_name}' not found in reference data.")
    return extracted_name

def normalize_team_name(extracted_name):
    """Attempts to find a matching team in the DB by name or abbr.
       Returns the normalized name or the original if no match.
    """
    if not extracted_name:
        return None
    # Try matching abbreviation first, then name
    team = Team.query.filter(Team.abbreviation.ilike(extracted_name)).first()
    if team:
        return team.name
    team = Team.query.filter(Team.name.ilike(f'%{extracted_name}%')).first()
    if team:
        return team.name
    print(f"Warning: Team '{extracted_name}' not found in reference data.")
    return extracted_name

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
        'card_set': None,
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
                mapped_data['card_year'] = int(year_match.group(1))
                # Remove year from title for further parsing
                title = title.replace(year_match.group(0), '').strip()
            except ValueError:
                pass

        # Extract Card Number
        number_match = NUMBER_PATTERN.search(title)
        if number_match:
            mapped_data['card_number'] = number_match.group(1)
            title = title.replace(number_match.group(0), '').strip()

        # Attempt to identify Player Name (often at the start or end)
        # This is very basic - needs matching against our Player table
        potential_player = title.split('-')[0].strip() # Very naive assumption
        mapped_data['player_name'] = normalize_player_name(potential_player)

        # Attempt to identify Team (often at the end)
        # This is also naive
        potential_team = title.split(' ')[-1]
        if potential_team.lower() != mapped_data['player_name'].split(' ')[-1].lower(): # Avoid matching last name as team
             mapped_data['team'] = normalize_team_name(potential_team)

        # Attempt to identify Set (needs list of known sets)
        # TODO: Implement set identification logic (e.g., check for 'Hoops', 'Prizm', etc.)
        mapped_data['card_set'] = "Unknown Set (Parsing Needed)" # Placeholder

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

    # --- Get Image URL ---
    # Use the thumbnail or primary image
    if item.get('image') and item['image'].get('imageUrl'):
        mapped_data['image_url'] = item['image'].get('imageUrl')
    elif item.get('thumbnailImages') and item['thumbnailImages'][0].get('imageUrl'):
        mapped_data['image_url'] = item['thumbnailImages'][0].get('imageUrl')

    # Basic validation - require at least a player name
    if not mapped_data['player_name']:
        print("Failed to extract player name from eBay data.")
        return None

    print(f"Mapped Data: {mapped_data}")
    return mapped_data

def save_card_from_data(mapped_data, user_id):
    """Creates and saves a Card object from mapped data.

    Args:
        mapped_data (dict): Dictionary returned by map_ebay_result_to_card_data.
        user_id (int): The ID of the owner user.

    Returns:
        Card: The newly created and saved Card object, or None if error.
    """
    if not mapped_data or not user_id:
        print("Error: Missing mapped data or user ID for saving card.")
        return None

    try:
        new_card = Card(
            owner_id=user_id,
            player_name=mapped_data.get('player_name'), # Should be validated earlier
            card_year=mapped_data.get('card_year'),
            card_set=mapped_data.get('card_set'),
            card_number=mapped_data.get('card_number'),
            team=mapped_data.get('team'),
            grade=mapped_data.get('grade'),
            image_url=mapped_data.get('image_url')
            # notes can be added later via update
            # date_added is default
        )
        db.session.add(new_card)
        db.session.commit()
        print(f"Successfully saved Card ID: {new_card.id}")
        return new_card
    except Exception as e:
        db.session.rollback() # Rollback in case of error during commit
        print(f"Error saving card to database: {e}")
        return None

# TODO: Add function to create/save Card object from mapped_data 