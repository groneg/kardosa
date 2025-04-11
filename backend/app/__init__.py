from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from config import Config

# Initialize extensions (but don't connect them to the app yet)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# User loader callback required by Flask-Login
# Must be defined *before* create_app or imported if defined elsewhere
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS with support for credentials (cookies) - More explicit config
    CORS(app,
         origins=["http://localhost:3000", "https://kardosa.xyz"], # Allow specific origins (local dev and production)
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Allow common methods
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"], # Allow common headers
         supports_credentials=True # Allow cookies
        )

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints here (if we split routes into multiple files)
    # Example: from app.main import bp as main_bp
    # app.register_blueprint(main_bp)

    # Import routes at the bottom to avoid circular imports
    # Note: If routes are defined in this file, they'd go here.
    # If they are in a separate file like routes.py, they need to be imported.
    with app.app_context():
        from . import routes, models # Ensure models are imported
        # Load reference data into memory cache on startup
        try:
            from .services import load_reference_data_cache
            print("Attempting to load reference data cache...") # Add logging
            load_reference_data_cache()
            print("Successfully loaded reference data cache.") # Add logging
        except Exception as e: # Catch broad exceptions during initial load
            print(f"WARNING: Could not load reference data cache during startup: {e}")
            print("WARNING: App will continue starting. Cache can be loaded later or on next request.")
            # Don't re-raise the exception, allow the app to start

    @app.route('/test/') # A simple test route directly in the factory
    def test_page():
        return '<h1>Testing the Flask Application Factory</h1>'

    return app 