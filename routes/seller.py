from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.db import db
from models.product import Product
from models.ProductReview import ProductReview 
from models.campaign import Campaign
from models.message import Message
from models.order import Order
from models.review import Review
from config import UPLOAD_FOLDER
from utils.helpers import save_file
import os
from datetime import datetime

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")

# ===================== HELPER =====================
def check_login():
    seller_id = session.get("user_id")
    if not seller_id:
        flash("Please log in first!", "danger")
        return None
    return seller_id

# ===================== DASHBOARD =====================
@seller_bp.route("/dashboard")
def dashboard():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    total_products = Product.query.filter_by(seller_id=seller_id).count()
    total_campaigns = Campaign.query.filter_by(seller_id=seller_id).count()
    total_sales = sum([o.quantity for o in Order.query.join(Order.product)
                       .filter(Product.seller_id == seller_id).all()])
    conversion_rate = round((total_sales / total_products) * 100, 2) if total_products > 0 else 0
    total_messages = Message.query.filter_by(receiver_id=seller_id).count()

    return render_template(
        "dashboard_seller.html",
        total_products=total_products,
        total_campaigns=total_campaigns,
        total_sales=total_sales,
        conversion_rate=conversion_rate,
        total_messages=total_messages
    )

# ===================== PRODUCTS =====================
@seller_bp.route("/products")
def products():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    products = Product.query.filter_by(seller_id=seller_id).all()
    return render_template("products.html", products=products)

@seller_bp.route("/add-product", methods=["GET", "POST"])
def add_product():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        stock = request.form.get("stock")

        if not (name and description and price and stock):
            flash("All fields are required!", "danger")
            return redirect(request.url)

        image_file = request.files.get("image")
        filename = None
        if image_file and image_file.filename != "":
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = save_file(image_file, UPLOAD_FOLDER)

        product = Product(
            name=name,
            description=description,
            price=float(price),
            stock=int(stock),
            image=filename,
            seller_id=seller_id
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("seller.products"))

    return render_template("add_product.html")

@seller_bp.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    product = Product.query.filter_by(id=id, seller_id=seller_id).first_or_404()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        stock = request.form.get("stock")

        if not (name and description and price and stock):
            flash("All fields are required!", "danger")
            return redirect(request.url)

        product.name = name
        product.description = description
        product.price = float(price)
        product.stock = int(stock)

        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            product.image = save_file(image_file, UPLOAD_FOLDER)

        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for("seller.products"))

    return render_template("edit_product.html", product=product)

@seller_bp.route("/delete-product/<int:id>", methods=["POST"])
def delete_product(id):
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    product = Product.query.filter_by(id=id, seller_id=seller_id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("seller.products"))

# ===================== CAMPAIGNS =====================
@seller_bp.route("/campaigns")
def campaigns():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    campaigns = Campaign.query.filter_by(seller_id=seller_id).all()
    return render_template("campaigns.html", campaigns=campaigns)

@seller_bp.route("/add-campaign", methods=["GET", "POST"])
def add_campaign():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        discount = request.form.get("discount")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not (name and discount and start_date and end_date):
            flash("All fields are required!", "danger")
            return redirect(request.url)

        try:
            campaign = Campaign(
                seller_id=seller_id,
                name=name.strip(),
                discount=float(discount),
                description=description.strip() if description else None,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d")
            )
            db.session.add(campaign)
            db.session.commit()
            flash("Campaign created successfully!", "success")
            return redirect(url_for("seller.campaigns"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("add_campaign.html")

@seller_bp.route("/edit-campaign/<int:id>", methods=["GET", "POST"])
def edit_campaign(id):
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    campaign = Campaign.query.filter_by(id=id, seller_id=seller_id).first_or_404()

    if request.method == "POST":
        name = request.form.get("name")
        discount = request.form.get("discount")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not (name and discount and start_date and end_date):
            flash("All fields are required!", "danger")
            return redirect(request.url)

        try:
            campaign.name = name.strip()
            campaign.discount = float(discount)
            campaign.description = description.strip() if description else None
            campaign.start_date = datetime.strptime(start_date, "%Y-%m-%d")
            campaign.end_date = datetime.strptime(end_date, "%Y-%m-%d")
            db.session.commit()
            flash("Campaign updated successfully!", "success")
            return redirect(url_for("seller.campaigns"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("edit_campaign.html", campaign=campaign)

@seller_bp.route("/delete-campaign/<int:id>", methods=["POST"])
def delete_campaign(id):
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    campaign = Campaign.query.filter_by(id=id, seller_id=seller_id).first_or_404()
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted successfully!", "success")
    return redirect(url_for("seller.campaigns"))

# ===================== MESSAGES =====================
@seller_bp.route("/messages")
def messages():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    messages = Message.query.filter_by(receiver_id=seller_id).all()
    return render_template("messages.html", messages=messages)

@seller_bp.route("/reply-message/<int:id>", methods=["POST"])
def reply_message(id):
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    msg = Message.query.filter_by(id=id, receiver_id=seller_id).first_or_404()
    reply_content = request.form.get("reply")
    if not reply_content:
        flash("Reply cannot be empty!", "danger")
        return redirect(url_for("seller.messages"))

    msg.body += f"\n\n[Seller Reply]: {reply_content}"
    db.session.commit()
    flash("Replied to message successfully!", "success")
    return redirect(url_for("seller.messages"))

# ===================== ORDERS =====================
@seller_bp.route("/orders")
def orders():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    orders = Order.query.join(Order.product).filter(Product.seller_id==seller_id).all()
    return render_template("orders.html", orders=orders)

@seller_bp.route("/reviews")
def reviews():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    # Use ProductReview model, not Review
    reviews = ProductReview.query.join(ProductReview.product).filter(Product.seller_id == seller_id).all()
    
    return render_template("reviews.html", reviews=reviews)


# ===================== ANALYTICS =====================
@seller_bp.route("/analytics")
def analytics():
    seller_id = check_login()
    if not seller_id:
        return redirect(url_for("auth.login"))

    products = Product.query.filter_by(seller_id=seller_id).all()
    return render_template("analytics.html", products=products)
