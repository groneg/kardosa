from flask import current_app, jsonify, request, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Card, Player, Team, Token
from werkzeug.utils import secure_filename
from .auth import token_required
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
    # Accept either username or email as the identifier
    identifier = data.get('username') or data.get('email')
    if not data or not identifier or not data.get('password'):
        return jsonify({'error': 'Missing username/email or password'}), 400

    # --- Debugging --- 
    print(f"Attempting login for identifier: '{identifier}'")
    print(f"Password received (type: {type(data.get('password'))}): '{data.get('password')}'")
    # ----------------

    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

    # --- Debugging --- 
    if user:
        print(f"User found: {user.username}")
        password_check_result = user.check_password(data['password'])
        print(f"Password check result: {password_check_result}")
    else:
        print("User not found in database.")
    # ----------------

    if user is None or not user.check_password(data['password']):
        print("Login failed due to user being None or password check failure.") # Debug
        return jsonify({'error': 'Invalid username or password'}), 401

    # Use Flask-Login to establish session (for backward compatibility)
    login_user(user) # Sets the session cookie
    
    # Generate a new UUID token for the user
    token = user.generate_auth_token()
    
    print("Login successful, setting session cookie and generating UUID token.") # Debug
    return jsonify({
        'message': 'Login successful', 
        'user_id': user.id,
        'token': token  # Return the token to the client
    }), 200

@current_app.route('/logout', methods=['POST'])
@token_required # Use our custom token authentication
def logout(current_user):
    # Clear any active tokens for this user (optional)
    # This is a security feature that invalidates all existing tokens
    # Remove this if you want tokens to remain valid until they expire
    if request.headers.get('Authorization'):
        token_str = request.headers.get('Authorization').split(' ')[1]
        token = Token.query.filter_by(token=token_str).first()
        if token:
            token.is_revoked = True
            db.session.commit()
            
    # Also log out via Flask-Login for backward compatibility
    logout_user() # Clears the session cookie
    return jsonify({"message": "Logout successful"}), 200

@current_app.route('/user', methods=['GET'])
@token_required
def get_current_user(current_user):
    # Returns information about the currently authenticated user
    
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    }), 200

# --- Single Card Upload Route --- CORRECTED

@current_app.route('/upload-single-card', methods=['POST'])
@token_required
def upload_single_card_image(current_user):
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
                # Get the parent folder name (timestamp folder) and the filename
                parent_folder = os.path.basename(os.path.dirname(save_path))
                filename = os.path.basename(save_path)
                # Fix image path to include /uploads and the timestamp folder
                mapped_data['image_url'] = f"/uploads/{parent_folder}/{filename}"  # Use the user's original card image with correct path
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
@token_required
def upload_binder_image(current_user):
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
        base_filename = os.path.splitext(unique_filename)[0]
        split_output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], base_filename + '_cards')
        
        try:
            # Save original binder image
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            print(f"Binder page saved to: {save_path}")

            # Extract cards
            extracted_card_paths = split_binder_page_by_grid(save_path, split_output_dir, inner_crop_percent=3)

            if not extracted_card_paths:
                return jsonify({'error': 'Failed to extract cards from image'}), 400

            processed_cards_results = []
            errors = []

            for i, card_path in enumerate(extracted_card_paths):
                try:
                    # Get relative path for storage in DB
                    relative_path = os.path.relpath(
                        card_path, 
                        current_app.config['UPLOAD_FOLDER']
                    ).replace('\\', '/')
                    
                    # eBay lookup and processing
                    ebay_result = find_card_on_ebay(card_path)
                    if not ebay_result:
                        errors.append(f"Card {i+1}: eBay lookup failed.")
                        continue

                    # Map data and save to DB
                    mapped_data = map_ebay_result_to_card_data(ebay_result)
                    if not mapped_data:
                        errors.append(f"Card {i+1}: Failed to map data from eBay result.")
                        continue

                    # Use the relative path for image_url, ensuring it has /uploads prefix
                    mapped_data['image_url'] = f"/uploads/{relative_path}"
                    newly_saved_card = save_card_from_data(mapped_data, user_id)
                    
                    if newly_saved_card:
                        processed_cards_results.append({
                            'source_image': relative_path,
                            'saved_card_id': newly_saved_card.id,
                            'player_name': newly_saved_card.player_name
                        })
                    else:
                        errors.append(f"Card {i+1}: Failed to save to database.")

                except Exception as card_e:
                    errors.append(f"Card {i+1}: {str(card_e)}")

            return jsonify({
                'message': f"Processed {len(processed_cards_results)} cards successfully",
                'saved_cards': processed_cards_results,
                'errors': errors
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

# --- Public Read-Only Collection Route ---

@current_app.route('/public/collection/<username>', methods=['GET'])
def public_collection(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    # Get all cards for this user
    cards = Card.query.filter_by(owner_id=user.id).all()
    # Serialize cards, excluding sensitive/user-only fields
    card_list = [
        {
            'id': card.id,
            'player': card.player_name,
            'team': card.team,
            'year': card.card_year,
            'manufacturer': card.manufacturer,
            'image_url': card.image_url,
            'date_added': card.date_added.isoformat() if card.date_added else None,
            # Add other public fields as needed
        } for card in cards
    ]
    return jsonify({'username': user.username, 'cards': card_list}), 200

@current_app.route('/public/collection/<username>/<int:card_id>', methods=['GET'])
def public_card_detail(username, card_id):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    card = Card.query.filter_by(id=card_id, owner_id=user.id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    card_data = {
        'id': card.id,
        'player_name': card.player_name,
        'card_year': card.card_year,
        'manufacturer': card.manufacturer,
        'card_number': card.card_number,
        'team': card.team,
        'grade': card.grade,
        'image_url': card.image_url,
        'date_added': card.date_added.isoformat() if card.date_added else None,
        'notes': card.notes,
        'sport': getattr(card, 'sport', None)
    }
    return jsonify({'card': card_data}), 200

# --- Card Management Routes (Flask-Login) ---

@current_app.route('/cards', methods=['GET'])
@token_required
def get_cards(current_user):
    # The token_required decorator already handles authentication and passes the user
    
    # Debug logging
    print(f"User authenticated successfully, ID: {current_user.id}")

    user_id = current_user.id
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
@token_required
def create_card(current_user):
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
@token_required
def get_card(card_id, current_user):
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
@token_required
def update_card(card_id, current_user):
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
@token_required
def delete_card(card_id, current_user):
    user_id = current_user.id
    card = Card.query.get_or_404(card_id)

    # TODO: Add ownership check
    if card.owner_id != user_id:
        return jsonify({"error": "Not authorized to delete this card"}), 403 # Forbidden

    db.session.delete(card)
    db.session.commit()

    return jsonify({"message": "Card deleted successfully"}), 200

@current_app.route('/autocomplete-options', methods=['GET'])
@token_required
def get_autocomplete_options(current_user):
    user_id = current_user.id
    try:
        # Get all cards for the current user
        user_cards = Card.query.filter_by(owner_id=user_id).all()
        
        # Extract unique values from user cards
        player_names = sorted(list(set(card.player_name for card in user_cards if card.player_name)))
        manufacturers = sorted(list(set(card.manufacturer for card in user_cards if card.manufacturer)))
        grades = sorted(list(set(card.grade for card in user_cards if card.grade)))

        # Only use teams from the Team table
        teams = [team.name for team in Team.query.order_by(Team.name).all()]

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

# Route to serve uploaded images
@current_app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Add more routes here as needed 