from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import JSON
from datetime import datetime

class Sitter(db.Model):
    __tablename__ = "sitters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), default="Not Provided")
    password_hash = db.Column(db.String(128))
    service_types = db.Column(JSON, default=list)  # e.g., ["Dog Walking", "Pet Sitting"]
    verification_status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    profile_image = db.Column(db.String(200), default="default-avatar.png")
    id_document = db.Column(db.String(200))
    selfie_with_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", back_populates="sitter", lazy="joined", cascade="all, delete-orphan")
    pricing_rules = db.relationship("PricingRule", back_populates="sitter", lazy="joined", cascade="all, delete-orphan")
    reviews = db.relationship("SitterReview", back_populates="sitter", lazy="joined", cascade="all, delete-orphan")

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Admin approval property
    @property
    def is_verified(self):
        return self.verification_status == "approved"

    # Display status nicely
    def display_status(self):
        return self.verification_status.capitalize()

    def __repr__(self):
        return f"<Sitter {self.name} - Status: {self.verification_status}>"

class SitterReview(db.Model):
    __tablename__ = "sitter_reviews"

    id = db.Column(db.Integer, primary_key=True)
    sitter_id = db.Column(db.Integer, db.ForeignKey("sitters.id"), nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to Sitter
    sitter = db.relationship("Sitter", back_populates="reviews")

    def __repr__(self):
        return f"<SitterReview {self.rating}/5 by {self.owner_name}>"
