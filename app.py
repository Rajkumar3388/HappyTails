from flask import Flask
from config import *
from utils.db import db
from flask_migrate import Migrate
from flask_mail import Mail

# Blueprints
from routes.auth import auth_bp
from routes.owner import owner_bp
from routes.sitter import sitter_bp
from routes.seller import seller_bp
from routes.community import community_bp
from routes.admin import admin_bp
from routes.main import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    # Initialize DB
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize Mail
    mail = Mail(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(sitter_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
