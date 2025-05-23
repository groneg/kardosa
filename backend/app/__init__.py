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

    # Load CORS configuration from environment or use defaults
    # For local development, we'll make it handle any localhost/127.0.0.1 origin
    dev_origins = [
        'http://localhost:3000',    # Regular local frontend
        'http://127.0.0.1:3000',    # IPv4 equivalent 
        'http://localhost:8080',    # Alternative port
        'http://127.0.0.1:8080',    # Alternative port IPv4
        'http://localhost:56213',   # Preview port
        'http://127.0.0.1:56213',   # Preview port IPv4
        'http://localhost:54439',   # Another preview port
        'http://127.0.0.1:54439',   # Another preview port IPv4
        # Add any range of ports for development
    ]
    
    # Add wildcard port ranges for local development
    for port in range(50000, 60000):
        dev_origins.append(f'http://localhost:{port}')
        dev_origins.append(f'http://127.0.0.1:{port}')

    # Production origins
    prod_origins = ['https://kardosa.xyz']
    
    # Choose origins based on environment
    origins = prod_origins if app.config.get('ENV') == 'production' else dev_origins
    
    # Apply CORS configuration
    CORS(app,
         origins=origins,  # Use the appropriate origins list
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True  # Allow cookies/credentials
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
            load_reference_data_cache() # Re-enabled after migration fix
        except Exception as e:
            print(f"Error loading reference data cache: {e}")
            # Consider how to handle this - app might not function correctly

    @app.route('/test/') # A simple test route directly in the factory
    def test_page():
        return '<h1>Testing the Flask Application Factory</h1>'

    return app 