from utils.db import db
from datetime import datetime

class Playdate(db.Model):
    __tablename__ = "playdates"

    id = db.Column(db.Integer, primary_key=True)

    # ===================== Requester (owner + pet) =====================
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=False)

    # ===================== Invitee (owner + pet) =====================
    invitee_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    invitee_pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=False)

    # ===================== Playdate Details =====================
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Enum('Pending', 'Accepted', 'Declined', name="playdate_status"), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ===================== Relationships =====================
    owner = db.relationship("User", foreign_keys=[owner_id], backref="sent_playdates")
    pet = db.relationship("Pet", foreign_keys=[pet_id])
    invitee_owner = db.relationship("User", foreign_keys=[invitee_owner_id], backref="received_playdates")
    invitee_pet = db.relationship("Pet", foreign_keys=[invitee_pet_id])

    # ===================== Representation =====================
    def __repr__(self):
        return f"<Playdate {self.pet.name} with {self.invitee_pet.name} on {self.date}>"
