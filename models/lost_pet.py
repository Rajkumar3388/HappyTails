from utils.db import db
from datetime import datetime
from models.user import User  # make sure User is imported

class LostPet(db.Model):
    __tablename__ = "lost_pet"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", backref="lost_pets")

    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    breed = db.Column(db.String(100))
    color = db.Column(db.String(50))
    last_seen = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Lost")
    reward = db.Column(db.Integer, default=0)  # optional reward
    image = db.Column(db.String(200))          # pet photo path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ⚡ Add this for community sightings
    sightings = db.relationship("Sighting", backref="lost_pet", lazy="dynamic")
