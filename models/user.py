from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="owner")  # owner, sitter, seller, guest

    # Relationships
    pets = db.relationship("Pet", back_populates="owner", lazy="joined", cascade="all, delete-orphan")
    products = db.relationship("Product", back_populates="seller", lazy="joined", cascade="all, delete-orphan")
    # Removed sitter_bookings from here because Booking.sitter_id points to Sitter.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
