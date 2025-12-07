from utils.db import db

class Availability(db.Model):
    __tablename__ = "availabilities"

    id = db.Column(db.Integer, primary_key=True)
    sitter_id = db.Column(db.Integer, db.ForeignKey("sitters.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.String(255))

    # Relationships
    sitter = db.relationship("Sitter", backref=db.backref("availabilities", lazy=True))
    bookings = db.relationship("Booking", back_populates="availability")  # <- make plural to match Booking

    def __repr__(self):
        return f"<Availability {self.id}: Sitter {self.sitter_id} on {self.date} {self.start_time}-{self.end_time}>"
