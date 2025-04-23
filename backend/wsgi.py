from app import create_app
from flask_cors import CORS

app = create_app()

# Apply CORS directly to the application instance
CORS(app, 
     origins=['https://kardosa.xyz', 'https://www.kardosa.xyz'],
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     expose_headers=['Content-Type', 'Authorization'])

if __name__ == '__main__':
    app.run()
