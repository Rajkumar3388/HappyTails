from utils.db import db
from datetime import datetime

class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)

    # Basic details
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.Enum('Dog', 'Cat', 'Bird', 'Other'), nullable=False)
    breed = db.Column(db.String(100), nullable=True)

    # Attributes
    age = db.Column(db.Integer, nullable=False)
    medical_history = db.Column(db.Text, nullable=True)

    # Image
    image = db.Column(db.String(200), nullable=True)  # store filename from uploads/

    # Relationship with user (pet owner)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship(
        "User",
        back_populates="pets",
        lazy="joined"
    )

    # Relationships with bookings
    bookings = db.relationship(
        "Booking",
        back_populates="pet",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # Relationships with playdates
    playdates_as_owner = db.relationship(
        "Playdate",
        foreign_keys="Playdate.pet_id",
        back_populates="pet",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    playdates_as_invitee = db.relationship(
        "Playdate",
        foreign_keys="Playdate.invitee_pet_id",
        back_populates="invitee_pet",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # Meta info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: ensure each owner can’t have two pets with the same name
    __table_args__ = (
        db.UniqueConstraint('owner_id', 'name', name='uq_owner_petname'),
    )

    def __repr__(self):
        return f"<Pet {self.name} ({self.species})>"
