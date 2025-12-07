from utils.db import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales_count = db.Column(db.Integer, default=0)

    # Relationship with User (seller)
    seller = db.relationship(
        "User",
        back_populates="products",  # matches User.products
        lazy="joined"  # eager-load seller when loading product
    )

    def __repr__(self):
        return f"<Product {self.name} by Seller {self.seller.name if self.seller else self.seller_id}>"
