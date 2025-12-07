from utils.db import db
from datetime import datetime

class Sighting(db.Model):
    __tablename__ = "sightings"

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("lost_pet.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Pet owner
    helper_name = db.Column(db.String(100), nullable=False)   # Name of the helper
    helper_phone = db.Column(db.String(20), nullable=False)   # Phone number of helper
    confidence = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
