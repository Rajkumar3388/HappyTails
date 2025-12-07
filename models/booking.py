from utils.db import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=False)
    sitter_id = db.Column(db.Integer, db.ForeignKey("sitters.id"), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey("availabilities.id"), nullable=True)
    status = db.Column(db.String(50), default="pending")
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    pet = db.relationship("Pet", back_populates="bookings", lazy="joined")
    sitter = db.relationship("Sitter", back_populates="bookings", lazy="joined")
    availability = db.relationship("Availability", back_populates="bookings", lazy="joined")

    # Owner via Pet
    @property
    def owner(self):
        return self.pet.owner if self.pet else None

    def __repr__(self):
        return f"<Booking {self.id}: Pet {self.pet_id} with Sitter {self.sitter_id}>"
