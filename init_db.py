# init_db.py
from utils.db import db   # import your SQLAlchemy instance
from app import app       # import your Flask app
# import your models here so SQLAlchemy knows about them
from models.user import User  # adjust if your User model is elsewhere

with app.app_context():
    db.create_all()  # create all tables
    print("✅ Database tables created successfully!")
