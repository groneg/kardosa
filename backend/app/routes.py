from flask import current_app, jsonify, request, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Card, Player, Team
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone
from .image_utils import split_binder_page, split_binder_page_by_grid
from .ebay_client import find_card_on_ebay
from .services import map_ebay_result_to_card_data, save_card_from_data, format_season_year, parse_season_year

# Helper function for uploads
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# This registers routes with the app created in __init__.py
# If using Blueprints, you would import and register the Blueprint instead.

@current_app.route('/')
def index():
    return jsonify({"message": "Kardosa backend is running!"})

# --- Authentication Routes (Flask-Login) ---

@current_app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing username, email, or password'}), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    # In a real app, you might log the user in immediately or send a confirmation email
    return jsonify({'message': 'User registered successfully'}), 201 # 201 Created

@current_app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Use Flask-Login to establish session
    login_user(user) # Sets the session cookie
    return jsonify({'message': 'Login successful', 'user_id': user.id}), 200

@current_app.route('/logout', methods=['POST'])
@login_required # Protect logout route
def logout():
    logout_user() # Clears the session cookie
    return jsonify({"message": "Logout successful"}), 200

@current_app.route('/user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    }), 200

# --- Single Card Upload Route --- CORRECTED

@current_app.route('/upload-single-card', methods=['POST'])
@login_required
def upload_single_card_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = current_user.id
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        unique_filename = f"single_{user_id}_{timestamp}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        try:
            file.save(save_path)
            print(f"Single card saved to: {save_path}")

            # --- eBay Lookup ---
            print(f"DEBUG: Triggering eBay lookup for single card: {save_path}")
            ebay_result = find_card_on_ebay(save_path)
            print(f"DEBUG: eBay lookup result: {ebay_result}")

            # --- Data Mapping ---
            mapped_data = None
            if ebay_result:
                mapped_data = map_ebay_result_to_card_data(ebay_result)

            # --- Save Card to DB ---
            newly_saved_card = None
            save_error = None
            if mapped_data:
                newly_saved_card = save_card_from_data(mapped_data, user_id)
                if not newly_saved_card:
                    save_error = "Failed to save mapped data to database."
            else:
                print("Could not map eBay data to card fields, skipping save.")
                save_error = "Could not map eBay data to card fields."
            # ---------------------

            # TODO: Maybe upload image to cloud storage?

            # Construct response based on outcome
            if newly_saved_card:
                response_message = f"Card (ID: {newly_saved_card.id}) created successfully from eBay data."
                response_status = 201
            else:
                response_message = f"Upload processed, but card not saved. Reason: {save_error or 'Unknown error'}"
                response_status = 202 # 202 Accepted, but not fully processed

            return jsonify({
                'message': response_message,
                'filename': unique_filename,
                'mapped_data': mapped_data,
                'saved_card_id': newly_saved_card.id if newly_saved_card else None
            }), response_status
        except Exception as e:
            print(f"Error saving or processing single card file: {e}")
            # Consider adding more specific error logging here
            return jsonify({'error': 'Failed to save or process file on server'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

# --- Binder Image Upload Route ---
@current_app.route('/upload-binder', methods=['POST'])
@login_required
def upload_binder_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = current_user.id
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        processed_cards_results = [] # Store results for each card
        errors = []

        try:
            file.save(save_path)
            print(f"Binder page saved to: {save_path}")

            # --- Call GRID image splitting (with 3% crop) --- 
            base_filename = os.path.splitext(unique_filename)[0]
            split_output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], base_filename + '_cards')
            extracted_card_paths = split_binder_page_by_grid(save_path, split_output_dir, inner_crop_percent=3)

            if not extracted_card_paths:
                errors.append("Failed to extract any cards from the binder page image (using grid method).")
            else:
                print(f"Extracted {len(extracted_card_paths)} potential card images. Processing each...")
                # --- Process Each Extracted Card Synchronously ---
                for i, card_path in enumerate(extracted_card_paths):
                    print(f"--- Processing card {i+1} from {card_path} ---")
                    try:
                        # 1. eBay Lookup
                        ebay_result = find_card_on_ebay(card_path)
                        if not ebay_result:
                            errors.append(f"Card {i+1}: eBay lookup failed.")
                            continue

                        # 2. Data Mapping
                        mapped_data = map_ebay_result_to_card_data(ebay_result)
                        if not mapped_data:
                            errors.append(f"Card {i+1}: Failed to map data from eBay result.")
                            continue

                        # 3. Save to DB
                        newly_saved_card = save_card_from_data(mapped_data, user_id)
                        if newly_saved_card:
                            processed_cards_results.append({
                                'source_image': os.path.basename(card_path),
                                'saved_card_id': newly_saved_card.id,
                                'player_name': newly_saved_card.player_name
                            })
                        else:
                            errors.append(f"Card {i+1}: Failed to save mapped data to database.")

                    except Exception as card_e:
                        error_msg = f"Card {i+1}: Unexpected error during processing: {card_e}"
                        print(error_msg)
                        errors.append(error_msg)
                # --- End Processing Loop ---

            # Construct final response
            response_status = 201 if processed_cards_results else (202 if errors else 200)
            response_message = f"Binder processing complete. Saved {len(processed_cards_results)} cards."
            if errors:
                response_message += f" Encountered {len(errors)} errors."

            return jsonify({
                'message': response_message,
                'original_filename': unique_filename,
                'saved_cards': processed_cards_results,
                'processing_errors': errors
            }), response_status

        except Exception as e:
            # Handle exceptions during initial save or overall process
            print(f"Error saving or processing binder file: {e}")
            return jsonify({'error': 'Failed to save or process binder file on server'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

# --- Card Management Routes (Flask-Login) ---

@current_app.route('/cards', methods=['GET'])
@login_required # Use Flask-Login decorator
def get_cards():
    # Debug logging
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user ID: {current_user.id}")

    user_id = current_user.id # Use Flask-Login proxy
    user = User.query.get(user_id)
    if not user:
        print(f"User not found for ID: {user_id}")
        return jsonify({"error": "User not found"}), 404 # Should not happen if auth is correct

    # Using the relationship (lazy='dynamic' requires .all())
    try:
        user_cards = user.cards.order_by(Card.date_added.desc()).all()

        # Serialize the list of cards
        cards_list = []
        for card in user_cards:
            cards_list.append({
                'id': card.id,
                'player_name': card.player_name,
                'card_year': card.card_year,  # Use the string directly from DB
                'manufacturer': card.manufacturer,
                'card_number': card.card_number,
                'team': card.team,
                'grade': card.grade,
                'image_url': card.image_url,
                'date_added': card.date_added.isoformat(),
                'notes': card.notes,
                'sport': card.sport
            })

        print(f"Returning {len(cards_list)} cards for user {user_id}")
        return jsonify(cards_list), 200
    except Exception as e:
        # Print the full traceback to the backend console for debugging
        import traceback
        print(f"Error fetching cards: {e}")
        traceback.print_exc() # Add this for detailed error logging
        return jsonify({"error": "Internal server error while fetching cards"}), 500

@current_app.route('/cards', methods=['POST'])
@login_required # Use Flask-Login decorator
def create_card():
    user_id = current_user.id # Use Flask-Login proxy
    data = request.get_json()
    if not data or not data.get('player_name'):
        return jsonify({'error': 'Missing required card data (player_name)'}), 400

    # Extract card details from request data
    player_name = data.get('player_name')
    card_year = parse_season_year(data.get('card_year'))
    manufacturer = data.get('manufacturer')
    card_number = data.get('card_number')
    team = data.get('team')
    grade = data.get('grade')
    image_url = data.get('image_url')
    notes = data.get('notes', '')
    sport = data.get('sport')

    # Validate required fields
    if not all([player_name, card_year, manufacturer, card_number, team]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Create new card
    new_card = Card(
        player_name=player_name,
        card_year=card_year,
        manufacturer=manufacturer,
        card_number=card_number,
        team=team,
        grade=grade,
        image_url=image_url,
        notes=notes,
        sport=sport,
        owner_id=current_user.id,
        date_added=datetime.utcnow()
    )

    # Return card data in response
    card_data = {
        'id': new_card.id,
        'player_name': new_card.player_name,
        'card_year': format_season_year(new_card.card_year),
        'manufacturer': new_card.manufacturer,
        'card_number': new_card.card_number,
        'team': new_card.team,
        'grade': new_card.grade,
        'image_url': new_card.image_url,
        'date_added': new_card.date_added.isoformat(),
        'notes': new_card.notes,
        'sport': new_card.sport
    }
    return jsonify(card_data), 201 # 201 Created

@current_app.route('/cards/<int:card_id>', methods=['GET'])
@login_required # Use Flask-Login decorator
def get_card(card_id):
    user_id = current_user.id # Use Flask-Login proxy
    card = Card.query.get_or_404(card_id)

    # TODO: Add ownership check
    if card.owner_id != user_id:
        return jsonify({"error": "Not authorized to view this card"}), 403 # Forbidden

    # Serialize the card data
    try:
        card_data = {
            'id': card.id,
            'player_name': card.player_name,
            'card_year': card.card_year,  # Use the string directly from DB (already 'YYYY-YY' format)
            'manufacturer': card.manufacturer,
            'card_number': card.card_number,
            'team': card.team,
            'grade': card.grade,
            'image_url': card.image_url,
            'date_added': card.date_added.isoformat(),
            'notes': card.notes,
            'sport': card.sport
        }
        return jsonify(card_data), 200
    except Exception as e:
        import traceback
        print(f"Error fetching single card (ID: {card_id}): {e}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error while fetching card details"}), 500

@current_app.route('/cards/<int:card_id>', methods=['PUT'])
@login_required # Use Flask-Login decorator
def update_card(card_id):
    user_id = current_user.id # Use Flask-Login proxy
    card = Card.query.get_or_404(card_id)

    # TODO: Add ownership check
    if card.owner_id != user_id:
        return jsonify({"error": "Not authorized to modify this card"}), 403 # Forbidden

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Update fields if they are provided in the request data
    card.player_name = data.get('player_name', card.player_name)
    
    # Handle card_year conversion from YYYY-YY to integer
    if 'card_year' in data:
        card.card_year = parse_season_year(data['card_year'])
    
    card.manufacturer = data.get('manufacturer', card.manufacturer)
    card.card_number = data.get('card_number', card.card_number)
    card.team = data.get('team', card.team)
    card.grade = data.get('grade', card.grade)
    card.image_url = data.get('image_url', card.image_url)
    card.notes = data.get('notes', card.notes)
    card.sport = data.get('sport', card.sport)
    # owner_id and date_added should generally not be updated here

    db.session.commit()

    # Return updated card data
    card_data = {
        'id': card.id,
        'player_name': card.player_name,
        'card_year': format_season_year(card.card_year),  # Convert to YYYY-YY format
        'manufacturer': card.manufacturer,
        'card_number': card.card_number,
        'team': card.team,
        'grade': card.grade,
        'image_url': card.image_url,
        'date_added': card.date_added.isoformat(),
        'notes': card.notes,
        'sport': card.sport
    }
    return jsonify(card_data), 200

@current_app.route('/cards/<int:card_id>', methods=['DELETE'])
@login_required # Use Flask-Login decorator
def delete_card(card_id):
    user_id = current_user.id # Use Flask-Login proxy
    card = Card.query.get_or_404(card_id)

    # TODO: Add ownership check
    if card.owner_id != user_id:
        return jsonify({"error": "Not authorized to delete this card"}), 403 # Forbidden

    db.session.delete(card)
    db.session.commit()

    return jsonify({"message": "Card deleted successfully"}), 200

@current_app.route('/autocomplete-options', methods=['GET'])
@login_required
def get_autocomplete_options():
    user_id = current_user.id
    
    try:
        # Get all cards for the current user
        user_cards = Card.query.filter_by(owner_id=user_id).all()
        
        # Extract unique values for each field
        player_names = sorted(list(set(card.player_name for card in user_cards if card.player_name)))
        manufacturers = sorted(list(set(card.manufacturer for card in user_cards if card.manufacturer)))
        teams = sorted(list(set(card.team for card in user_cards if card.team)))
        grades = sorted(list(set(card.grade for card in user_cards if card.grade)))
        
        # Add some common grade options if not already present
        common_grades = ["Raw", "PSA 10", "PSA 9", "PSA 8", "PSA 7", "BGS 10", "BGS 9.5", "BGS 9", "SGC 10", "SGC 9"]
        for grade in common_grades:
            if grade not in grades:
                grades.append(grade)
        
        return jsonify({
            'player_names': player_names,
            'manufacturers': manufacturers,
            'teams': teams,
            'grades': grades
        }), 200
    except Exception as e:
        print(f"Error fetching autocomplete options: {e}")
        return jsonify({"error": "Internal server error while fetching autocomplete options"}), 500

# Add more routes here as needed 