import os
from dotenv import load_dotenv # Import load_dotenv

# Get the base directory of the backend application
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # Load .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-dev-key'
    # Add Session Cookie settings for Flask-Login & CORS
    # Force secure settings for deployment
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True # Prevent JS access to cookie
    # 'None' is needed for cross-site requests (like Vercel frontend -> Render backend)
    # Requires Secure=True
    SESSION_COOKIE_SAMESITE = 'None'

    # Domain Scope for Cookie (Crucial for cross-subdomain)
    SESSION_COOKIE_DOMAIN = '.kardosa.xyz'

    # Force secure settings for REMEMBER_COOKIE as well
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'None'
    # eBay API Config from .env
    EBAY_APP_ID = os.environ.get('EBAY_APP_ID')
    EBAY_DEV_ID = os.environ.get('EBAY_DEV_ID')
    EBAY_CERT_ID = os.environ.get('EBAY_CERT_ID')
    EBAY_ENV = os.environ.get('EBAY_ENV', 'SANDBOX') # Default to SANDBOX if not set
    # Define the SQLite database location
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    # Add other configuration variables as needed 