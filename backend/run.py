from app import create_app, db # Import db
from app.models import User # Import User model
import click # Import click for CLI arguments

# Create the Flask app instance using the factory
app = create_app()

# --- Temporary CLI command to create a user ---
@app.cli.command('create-user')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_user(username, email, password):
    """Creates a new user with username, email, and password."""
    if User.query.filter_by(username=username).first():
        print(f'Error: Username "{username}" already exists.')
        return
    if User.query.filter_by(email=email).first():
        print(f'Error: Email "{email}" already registered.')
        return

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'User "{username}" created successfully with ID: {user.id}')
# --- End of temporary command ---

if __name__ == '__main__':
    # Run the app in debug mode for development
    # Host='0.0.0.0' makes it accessible on the network
    app.run(host='0.0.0.0', port=5000, debug=True) 