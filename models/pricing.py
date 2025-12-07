from utils.db import db

class PricingRule(db.Model):
    __tablename__ = "pricing_rules"

    id = db.Column(db.Integer, primary_key=True)
    sitter_id = db.Column(db.Integer, db.ForeignKey("sitters.id"), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    pet_size = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    special_needs = db.Column(db.String(10), nullable=False, default="No")
    price = db.Column(db.Float, nullable=False)

    # Use string reference here too
    sitter = db.relationship("Sitter", back_populates="pricing_rules")
