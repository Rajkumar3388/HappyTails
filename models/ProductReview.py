from utils.db import db 
from datetime import datetime
class ProductReview(db.Model):
    __tablename__ = "product_review"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)  # plural
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)        # plural
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship("Product", backref="reviews")
    user = db.relationship("User", backref="product_reviews")
