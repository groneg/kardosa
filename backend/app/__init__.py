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
    prod_origins = ['https://kardosa.xyz', 'https://www.kardosa.xyz']
    
    import os
    import sys
    # Detect environment (use FLASK_ENV or ENV)
    env = os.environ.get('FLASK_ENV') or app.config.get('ENV') or 'production'

    if env == 'production':
        origins = ['https://kardosa.xyz', 'https://www.kardosa.xyz']
    else:
        # Local dev: allow localhost and 127.0.0.1 on any port
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ]
        # Optionally add wildcard ports for local dev
        for port in range(50000, 60000):
            origins.append(f'http://localhost:{port}')
            origins.append(f'http://127.0.0.1:{port}')

    print(f"[KARDOSA CORS DEBUG] ENV: {env}", file=sys.stderr)
    print(f"[KARDOSA CORS DEBUG] Using CORS origins: {origins}", file=sys.stderr)

    # Use UPLOAD_FOLDER from environment, default to '/tmp/uploads' for cloud, else local 'uploads' directory
    default_upload_dir = '/tmp/uploads' if os.environ.get('RENDER', None) or os.environ.get('DYNO', None) else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER') or default_upload_dir

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'])
            print(f"[KARDOSA INIT] Ensured uploads directory exists at: {app.config['UPLOAD_FOLDER']}", file=sys.stderr)
        except OSError as e:
            print(f"[KARDOSA INIT WARNING] Could not create uploads directory at {app.config['UPLOAD_FOLDER']}: {e}", file=sys.stderr)

    
    # *** PRODUCTION CORS FIX - RESTRICTED ORIGINS ***
    CORS(app, resources={r'/*': {'origins': origins}}, supports_credentials=True)
    
    # Visual breadcrumb to confirm this is being loaded
    @app.route('/cors-debug')
    def cors_debug_info():
        from flask import jsonify, request
        import os, datetime
        return jsonify({
            'status': 'CORS config check',
            'timestamp': str(datetime.datetime.now()),
            'environment': app.config.get('ENV'),
            'origins': origins,
            'request_origin': request.headers.get('Origin'),
            'init_py_loaded': True
        })
    

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