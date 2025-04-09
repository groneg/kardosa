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

    # Enable CORS with support for credentials (cookies)
    CORS(app, supports_credentials=True)

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
        from . import routes  # Import routes
        # You might also import models here if needed for initialization
        from . import models # Ensure models are imported for discovery by Flask-Migrate
        # db.create_all() # Uncomment this if you want to auto-create tables on startup (use migrations instead for prod)

    @app.route('/test/') # A simple test route directly in the factory
    def test_page():
        return '<h1>Testing the Flask Application Factory</h1>'

    return app 