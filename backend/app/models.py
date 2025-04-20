# Database models will be defined here using SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # Import UserMixin
from . import db  # Import the db instance from __init__.py

# Example:
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), index=True, unique=True)
#     email = db.Column(db.String(120), index=True, unique=True)
#     password_hash = db.Column(db.String(128))

#     def __repr__(self):
#         return f'<User {self.username}>' 

class User(db.Model, UserMixin): # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for stronger hashes

    # Relationship: One user has many cards
    # back_populates links this to the 'owner' relationship in Card
    # lazy='dynamic' means the query for cards isn't run until explicitly requested
    cards = db.relationship('Card', back_populates='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    # Add methods for password hashing/checking here later (e.g., using Werkzeug)
    def set_password(self, password):
        # Generate hash using pbkdf2:sha256 method with salt
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)
    card_year = db.Column(db.String(20), nullable=False)  # Changed from Integer to String to store YYYY-YY format
    manufacturer = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(50))
    team = db.Column(db.String(100))
    grade = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    sport = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: Many cards belong to one user
    # back_populates links this to the 'cards' relationship in User
    owner = db.relationship('User', back_populates='cards')

    def to_dict(self):
        return {
            'id': self.id,
            'player_name': self.player_name,
            'card_year': self.card_year,
            'manufacturer': self.manufacturer,
            'card_number': self.card_number,
            'team': self.team,
            'grade': self.grade,
            'image_url': self.image_url,
            'notes': self.notes,
            'sport': self.sport,
            'owner_id': self.owner_id,
            'date_added': self.date_added.isoformat() if self.date_added else None
        }

    def __repr__(self):
        return f'<Card {self.card_year} {self.manufacturer} {self.player_name} {self.card_number or ""}>'

# Potentially add Player and Team models here later for validation/enrichment

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    abbreviation = db.Column(db.String(10), unique=True, nullable=False, index=True)
    # city = db.Column(db.String(100)) # Could add if easily available

    def __repr__(self):
        return f'<Team {self.abbreviation}>'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    # first_active_year = db.Column(db.Integer, index=True)
    # last_active_year = db.Column(db.Integer, index=True)
    # Could add active years if derivable

    def __repr__(self):
        return f'<Player {self.full_name}>'

# Add CardSet model at the end of the file
class CardSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    year = db.Column(db.Integer, index=True, nullable=False)
    manufacturer = db.Column(db.String(100), nullable=True)
    sport = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<CardSet {self.name} ({self.year})>' 