from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.db import db
from models.user import User
from models.pet import Pet
from models.product import Product
from models.booking import Booking
from models.sitter import Sitter
from sqlalchemy.orm import joinedload
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ---------------- ADMIN CHECK DECORATOR ---------------- #
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("user_role") != "admin":
            flash("Please login as admin first!", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

# ---------------- DASHBOARD ---------------- #
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    users = User.query.all()
    pets = Pet.query.options(joinedload(Pet.owner)).all()
    products = Product.query.options(joinedload(Product.seller)).all()
    bookings = Booking.query.options(
        joinedload(Booking.pet),
        joinedload(Booking.sitter)
    ).all()
    sitters = Sitter.query.all()
    return render_template(
        "dashboard_admin.html",
        users=users,
        pets=pets,
        products=products,
        bookings=bookings,
        sitters=sitters
    )

# ---------------- SITTER LIST ---------------- #
@admin_bp.route("/sitters")
@admin_required
def sitter_list():
    sitters = Sitter.query.all()
    return render_template("admin_sitter_list.html", sitters=sitters)

# ---------------- SITTER PROFILE ---------------- #
@admin_bp.route("/sitter/<int:sitter_id>")
@admin_required
def sitter_profile(sitter_id):
    sitter = Sitter.query.get_or_404(sitter_id)
    return render_template("admin_sitter_profile.html", sitter=sitter)

# ---------------- VERIFY / REJECT SITTER ---------------- #
@admin_bp.route("/verify-sitter/<int:sitter_id>/<action>")
@admin_required
def verify_sitter(sitter_id, action):
    sitter = Sitter.query.get_or_404(sitter_id)

    if action not in ["approved", "rejected"]:
        flash("Invalid action", "danger")
        return redirect(url_for("admin.sitter_list"))

    sitter.verification_status = action
    sitter.verified = (action == "approved")
    db.session.commit()

    flash(f"Sitter {action} successfully!", "success")
    return redirect(url_for("admin.sitter_profile", sitter_id=sitter.id))

# ---------------- DELETE ROUTES ---------------- #
@admin_bp.route("/delete-user/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/delete-pet/<int:pet_id>")
@admin_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    flash("Pet deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/delete-product/<int:product_id>")
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/delete-sitter/<int:sitter_id>")
@admin_required
def delete_sitter(sitter_id):
    sitter = Sitter.query.get_or_404(sitter_id)
    db.session.delete(sitter)
    db.session.commit()
    flash("Sitter deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))
