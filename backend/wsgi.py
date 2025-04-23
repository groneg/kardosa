from app import create_app
from flask_cors import CORS

app = create_app()

# Completely disable CORS restrictions - allow everything
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

# Add middleware to force permissive headers on all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    app.run()
