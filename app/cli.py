import click
from app.extensions import db
from app.models import User


def init_cli(app):
    """Initialize CLI commands"""
    
    @app.cli.command('create-admin')
    @click.option('--username', prompt='Admin username', help='Username for the admin account')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the admin account')
    def create_admin(username, password):
        """Create a new admin account"""
        from werkzeug.security import generate_password_hash
        
        if User.query.filter_by(username=username).first():
            click.echo(click.style(f'Error: Username "{username}" already exists', fg='red'))
            return
        
        pw_hash = generate_password_hash(password)
        admin = User(username=username, password_hash=pw_hash, role='admin')
        db.session.add(admin)
        db.session.commit()
        
        click.echo(click.style(f'✓ Admin account "{username}" created successfully!', fg='green'))
        click.echo('You can now log in and invite other admins via the admin panel.')
