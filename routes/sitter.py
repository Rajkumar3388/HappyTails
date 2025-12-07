from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from utils.db import db
from models.user import User 
from models.pet import Pet
from models.sitter import Sitter, SitterReview
from models.pricing import PricingRule
from models.booking import Booking
from models.availability import Availability
from werkzeug.utils import secure_filename
import os

sitter_bp = Blueprint("sitter", __name__, url_prefix="/sitter")

# ---------------- UPLOAD FOLDERS ---------------- #
UPLOAD_FOLDER = os.path.join("static", "uploads")
ID_FOLDER = os.path.join(UPLOAD_FOLDER, "ids")
SELFIE_FOLDER = os.path.join(UPLOAD_FOLDER, "selfies")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ID_FOLDER, exist_ok=True)
os.makedirs(SELFIE_FOLDER, exist_ok=True)

# ---------------- HELPER ---------------- #
def sitter_login_required():
    sitter_id = session.get("user_id")
    role = session.get("user_role")
    if not sitter_id or role != "sitter":
        flash("Please login as sitter first!", "danger")
        return None
    return sitter_id

# ---------------- DASHBOARD ---------------- #
@sitter_bp.route("/dashboard")
def dashboard():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get(sitter_id)
    if not sitter:
        flash("Sitter not found.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("dashboard_sitter.html", sitter=sitter)

# ---------------- REGISTER SITTER ---------------- #
@sitter_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        # Validate inputs
        if not all([name, email, password]):
            flash("Name, email, and password are required!", "danger")
            return redirect(url_for("sitter.register"))

        # Check if sitter already exists
        existing = Sitter.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered!", "warning")
            return redirect(url_for("sitter.register"))

        # Create and hash password
        sitter = Sitter(
            name=name,
            email=email,
            phone=phone,
            service_types=[],
            verification_status="pending",
            profile_image="default-avatar.png"
        )
        sitter.set_password(password)  # ✅ this fixes your error

        db.session.add(sitter)
        db.session.commit()

        flash("Sitter registered successfully! Awaiting admin verification.", "success")
        return redirect(url_for("auth.login"))  # change to your login route name

    return render_template("sitter_register.html")


# ---------------- BOOKINGS ---------------- #
@sitter_bp.route("/bookings")
def bookings():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get(sitter_id)
    bookings = Booking.query.filter_by(sitter_id=sitter_id).all()
    return render_template("dashboard_sitter_bookings.html", sitter=sitter, bookings=bookings)

@sitter_bp.route("/booking/<int:id>/update/<action>")
def update_booking(id, action):
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    booking = Booking.query.get_or_404(id)
    if action not in ["approved", "completed", "rejected"]:
        flash("Invalid action", "danger")
        return redirect(url_for("sitter.bookings"))

    booking.status = action
    db.session.commit()
    flash(f"Booking {action} successfully", "success")
    return redirect(url_for("sitter.bookings"))

# ---------------- EDIT PROFILE ---------------- #
@sitter_bp.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)

    if request.method == "POST":
        sitter.name = request.form.get("name")
        sitter.email = request.form.get("email")
        sitter.phone = request.form.get("phone")
        sitter.service_types = request.form.getlist("service_types")
        # Admin controls verification, sitter cannot set it
        # sitter.verification_status = "pending"  # optional

        # Profile image
        file = request.files.get("profile_image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            sitter.profile_image = filename

        # ID document
        id_file = request.files.get("id_document")
        if id_file and id_file.filename:
            id_filename = secure_filename(id_file.filename)
            id_file.save(os.path.join(ID_FOLDER, id_filename))
            sitter.id_document = id_filename

        # Selfie with ID
        selfie_file = request.files.get("selfie_with_id")
        if selfie_file and selfie_file.filename:
            selfie_filename = secure_filename(selfie_file.filename)
            selfie_file.save(os.path.join(SELFIE_FOLDER, selfie_filename))
            sitter.selfie_with_id = selfie_filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("sitter.edit_profile"))

    return render_template("sitter_edit_profile.html", sitter=sitter)

# ---------------- PRICING ---------------- #
@sitter_bp.route("/set-pricing", methods=["GET"])
def set_pricing():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)
    pricing_rules = PricingRule.query.filter_by(sitter_id=sitter.id).all()
    return render_template("sitter_set_pricing.html", sitter=sitter, pricing_rules=pricing_rules)

@sitter_bp.route("/pricing/add", methods=["POST"])
def add_pricing():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)
    service_name = request.form.get("service_name")
    pet_size = request.form.get("pet_size")
    duration = request.form.get("duration")
    special_needs = request.form.get("special_needs")
    price = request.form.get("price")

    if not (service_name and pet_size and duration and price):
        flash("All fields are required!", "danger")
        return redirect(url_for("sitter.set_pricing"))

    rule = PricingRule(
        sitter_id=sitter.id,
        service_name=service_name,
        pet_size=pet_size,
        duration=int(duration),
        special_needs=special_needs,
        price=float(price)
    )
    db.session.add(rule)
    db.session.commit()
    flash("Pricing rule added successfully!", "success")
    return redirect(url_for("sitter.set_pricing"))

@sitter_bp.route("/pricing/update/<int:id>", methods=["POST"])
def update_pricing(id):
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    rule = PricingRule.query.filter_by(id=id, sitter_id=sitter_id).first_or_404()
    rule.service_name = request.form.get("service_name")
    rule.pet_size = request.form.get("pet_size")
    rule.duration = int(request.form.get("duration"))
    rule.special_needs = request.form.get("special_needs")
    rule.price = float(request.form.get("price"))

    db.session.commit()
    flash("Pricing rule updated successfully!", "success")
    return redirect(url_for("sitter.set_pricing"))

@sitter_bp.route("/pricing/delete/<int:id>")
def delete_pricing(id):
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    rule = PricingRule.query.filter_by(id=id, sitter_id=sitter_id).first_or_404()
    db.session.delete(rule)
    db.session.commit()
    flash("Pricing rule deleted successfully!", "success")
    return redirect(url_for("sitter.set_pricing"))

# ---------------- AVAILABILITY ---------------- #
@sitter_bp.route("/set-availability", methods=["GET", "POST"])
def set_availability():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)

    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        notes = request.form.get("notes")

        if not (date and start_time and end_time):
            flash("All fields are required!", "danger")
            return redirect(url_for("sitter.set_availability"))

        slot = Availability(
            sitter_id=sitter_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            notes=notes
        )
        db.session.add(slot)
        db.session.commit()
        flash("Availability added successfully!", "success")
        return redirect(url_for("sitter.set_availability"))

    availability_list = Availability.query.filter_by(sitter_id=sitter_id).all()
    return render_template("sitter_set_availability.html", sitter=sitter, availability_list=availability_list)

@sitter_bp.route("/delete_availability/<int:id>", methods=["POST"])
def delete_availability(id):
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    slot = Availability.query.filter_by(id=id, sitter_id=sitter_id).first_or_404()
    db.session.delete(slot)
    db.session.commit()
    flash("Availability slot deleted successfully!", "success")
    return redirect(url_for("sitter.set_availability"))

# ---------------- REVIEWS ---------------- #
@sitter_bp.route("/manage-reviews")
def manage_reviews():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)
    reviews = SitterReview.query.filter_by(sitter_id=sitter_id).order_by(SitterReview.created_at.desc()).all()
    return render_template("sitter_manage_reviews.html", sitter=sitter, reviews=reviews)

# ---------------- PLACEHOLDER ROUTES ---------------- #
@sitter_bp.route("/view-requests")
def view_requests():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)

    # Get all bookings for this sitter, eager load pet and owner
    bookings = Booking.query.filter_by(sitter_id=sitter_id).all()

    # No need to manually attach owner; access via booking.pet.owner in template
    return render_template("sitter_view_requests.html", sitter=sitter, bookings=bookings)



@sitter_bp.route("/view-payments")
def view_payments():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))
    sitter = Sitter.query.get_or_404(sitter_id)
    return render_template("sitter_view_payments.html", sitter=sitter)

@sitter_bp.route("/view-alerts")
def view_alerts():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))
    sitter = Sitter.query.get_or_404(sitter_id)
    return render_template("sitter_view_alerts.html", sitter=sitter)

@sitter_bp.route("/manage-bundles")
def manage_bundles():
    sitter_id = sitter_login_required()
    if not sitter_id:
        return redirect(url_for("auth.login"))
    sitter = Sitter.query.get_or_404(sitter_id)
    return render_template("sitter_manage_bundles.html", sitter=sitter)
