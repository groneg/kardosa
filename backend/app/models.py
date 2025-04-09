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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_name = db.Column(db.String(128), index=True, nullable=False)
    card_year = db.Column(db.Integer, index=True)
    card_set = db.Column(db.String(128), index=True)
    card_number = db.Column(db.String(20)) # e.g., "#12A", "NNO"
    team = db.Column(db.String(128), index=True)
    grade = db.Column(db.String(64), nullable=True) # e.g., "PSA 10", "BGS 9.5", "SGC 9", "Raw"
    image_url = db.Column(db.String(512), nullable=True) # URL to image in object storage
    date_added = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)

    # Relationship: Many cards belong to one user
    # back_populates links this to the 'cards' relationship in User
    owner = db.relationship('User', back_populates='cards')

    def __repr__(self):
        return f'<Card {self.card_year} {self.card_set} {self.player_name} {self.card_number or ""}>'

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