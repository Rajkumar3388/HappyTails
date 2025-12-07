from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import db
from models.pet import Pet
from models.product import Product
from models.playdate import Playdate
from models.user import User
from models.lost_pet import LostPet
from models.sighting import Sighting
from models.pricing import PricingRule
from models.sitter import Sitter, SitterReview
from models.availability import Availability
from models.booking import Booking
from models.order import Order
from models.ProductReview import ProductReview
from config import UPLOAD_FOLDER
from utils.helpers import save_file
import os
from datetime import datetime

owner_bp = Blueprint("owner", __name__, url_prefix="/owner")

# ===================== HELPER: CHECK LOGIN =====================
def check_login():
    user_id = session.get("user_id")
    role = session.get("role")  # 'owner' or 'sitter'
    if not user_id:
        flash("Please log in first!", "danger")
        return None, None
    return int(user_id), role

# ===================== DASHBOARD =====================
@owner_bp.route("/dashboard")
def dashboard():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    my_pets = Pet.query.filter_by(owner_id=user_id).all()
    other_pets = Pet.query.filter(Pet.owner_id != user_id).all()
    return render_template("dashboard_owner.html", my_pets=my_pets, other_pets=other_pets, role=role)

# ===================== PETS =====================
@owner_bp.route("/pets")
def pets():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pets = Pet.query.filter_by(owner_id=user_id).all()
    return render_template("owner_pets.html", pets=pets, role=role)

@owner_bp.route("/pet/<int:pet_id>")
def pet_detail(pet_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pet = Pet.query.filter_by(id=pet_id, owner_id=user_id).first_or_404()
    return render_template("owner_pet_detail.html", pet=pet, role=role)

@owner_bp.route("/pet/add", methods=["GET", "POST"])
def add_pet():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form["name"]
        species = request.form.get("species", "Other")
        breed = request.form["breed"]
        age = request.form["age"]
        medical_history = request.form.get("medical_history")
        image_file = request.files.get("image")
        filename = None
        if image_file and image_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = save_file(image_file, UPLOAD_FOLDER)

        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=age,
            medical_history=medical_history,
            image=filename,
            owner_id=user_id
        )
        db.session.add(pet)
        db.session.commit()
        flash("Pet added successfully!", "success")
        return redirect(url_for("owner.pets"))

    return render_template("owner_edit_pet.html", pet=None, role=role)

@owner_bp.route("/pet/edit/<int:pet_id>", methods=["GET", "POST"])
def edit_pet(pet_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pet = Pet.query.filter_by(id=pet_id, owner_id=user_id).first_or_404()
    if request.method == "POST":
        pet.name = request.form["name"]
        pet.species = request.form.get("species", pet.species)
        pet.breed = request.form["breed"]
        pet.age = request.form["age"]
        pet.medical_history = request.form.get("medical_history")
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            pet.image = save_file(image_file, UPLOAD_FOLDER)
        db.session.commit()
        flash("Pet updated successfully!", "success")
        return redirect(url_for("owner.pets"))

    return render_template("owner_edit_pet.html", pet=pet, role=role)

@owner_bp.route("/pet/delete/<int:pet_id>")
def delete_pet(pet_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pet = Pet.query.filter_by(id=pet_id, owner_id=user_id).first_or_404()
    db.session.delete(pet)
    db.session.commit()
    flash("Pet deleted successfully!", "success")
    return redirect(url_for("owner.pets"))

# ===================== PLAYDATES =====================
@owner_bp.route("/playdates", methods=["GET", "POST"])
def playdates():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    my_pets = Pet.query.filter_by(owner_id=user_id).all()
    other_pets = Pet.query.filter(Pet.owner_id != user_id).all()

    if request.method == "POST":
        try:
            pet_id = int(request.form["pet_id"])
            invitee_pet_id = int(request.form["invitee_pet_id"])
            date = request.form["date"]
            time = request.form["time"]
            location = request.form["location"]

            invitee_pet = Pet.query.get(invitee_pet_id)
            if not invitee_pet:
                flash("Selected pet does not exist!", "danger")
                return redirect(url_for("owner.playdates"))

            new_playdate = Playdate(
                owner_id=user_id,
                pet_id=pet_id,
                invitee_owner_id=invitee_pet.owner_id,
                invitee_pet_id=invitee_pet_id,
                date=date,
                time=time,
                location=location,
                status="Pending"
            )
            db.session.add(new_playdate)
            db.session.commit()
            flash("Playdate requested successfully!", "success")
        except Exception as e:
            flash(f"Error creating playdate: {str(e)}", "danger")
        return redirect(url_for("owner.playdates"))

    my_playdates = Playdate.query.filter(
        (Playdate.owner_id == user_id) | (Playdate.invitee_owner_id == user_id)
    ).order_by(Playdate.date.asc(), Playdate.time.asc()).all()

    return render_template("owner_playdates.html", my_pets=my_pets, other_pets=other_pets,
                           playdates=my_playdates, user_id=user_id, role=role)

@owner_bp.route("/playdates/accept/<int:playdate_id>")
def accept_playdate(playdate_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    playdate = Playdate.query.get_or_404(playdate_id)
    if user_id != playdate.invitee_owner_id:
        flash("You cannot accept this playdate.", "danger")
        return redirect(url_for("owner.playdates"))

    playdate.status = "Accepted"
    db.session.commit()
    flash(f"{playdate.invitee_pet.name} accepted the playdate!", "success")
    return redirect(url_for("owner.playdates"))

@owner_bp.route("/playdates/reject/<int:playdate_id>")
def reject_playdate(playdate_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    playdate = Playdate.query.get_or_404(playdate_id)
    if user_id != playdate.invitee_owner_id:
        flash("You cannot reject this playdate.", "danger")
        return redirect(url_for("owner.playdates"))

    playdate.status = "Declined"
    db.session.commit()
    flash(f"{playdate.invitee_pet.name} declined the playdate.", "warning")
    return redirect(url_for("owner.playdates"))

@owner_bp.route("/playdates/delete/<int:playdate_id>")
def delete_playdate(playdate_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    playdate = Playdate.query.filter_by(id=playdate_id, owner_id=user_id).first()
    if not playdate:
        flash("Playdate not found or you are not authorized!", "danger")
        return redirect(url_for("owner.playdates"))

    if playdate.status != "Pending":
        flash("You can only delete pending requests!", "warning")
        return redirect(url_for("owner.playdates"))

    db.session.delete(playdate)
    db.session.commit()
    flash("Playdate request deleted successfully!", "success")
    return redirect(url_for("owner.playdates"))

# ===================== LOST & FOUND =====================
@owner_bp.route("/lost-found")
def lost_found():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    my_lost_pets = LostPet.query.filter_by(owner_id=user_id).order_by(LostPet.created_at.desc()).all()
    other_lost_pets = LostPet.query.filter(LostPet.owner_id != user_id).order_by(LostPet.created_at.desc()).all()
    return render_template("owner_lost_found.html", my_lost_pets=my_lost_pets, other_lost_pets=other_lost_pets, role=role)

@owner_bp.route("/lost-pet-alerts")
def lost_pet_alerts():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    # Get all pets of this owner
    alerts = LostPet.query.filter_by(owner_id=user_id)\
                          .order_by(LostPet.created_at.desc())\
                          .all()

    for pet in alerts:
        # Fetch pending sightings as a list
        sightings_list = pet.sightings.filter_by(status="Pending")\
                                      .order_by(Sighting.created_at.desc())\
                                      .all()
        pet.sightings_count = len(sightings_list)
        pet.sightings_to_show = sightings_list  # use this in template

    return render_template("owner_lost_pet_alerts.html", alerts=alerts, role=role)




@owner_bp.route("/report-lost-pet", methods=["GET", "POST"])
def report_lost_pet():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        pet_name = request.form.get("pet_name")
        pet_type = request.form.get("pet_type")
        breed = request.form.get("breed")
        color = request.form.get("color")
        last_seen = request.form.get("last_seen")
        description = request.form.get("description")
        reward = request.form.get("reward", type=float)

        image_file = request.files.get("image")
        filename = None
        if image_file and image_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = save_file(image_file, UPLOAD_FOLDER)

        new_lost_pet = LostPet(
            owner_id=user_id,
            name=pet_name,
            type=pet_type,
            breed=breed,
            color=color,
            last_seen=last_seen,
            description=description,
            status="Lost",
            reward=reward,
            image=filename,
            created_at=datetime.utcnow()
        )
        db.session.add(new_lost_pet)
        db.session.commit()
        flash(f"Lost pet '{pet_name}' reported successfully!", "success")
        return redirect(url_for("owner.lost_found"))

    return render_template("owner_report_lost_pet.html", role=role)

@owner_bp.route("/lost-pet/<int:pet_id>")
def view_lost_pet(pet_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pet = LostPet.query.get_or_404(pet_id)
    sightings = Sighting.query.filter_by(pet_id=pet_id).order_by(Sighting.created_at.desc()).all()
    return render_template("owner_view_lost_pet.html", pet=pet, sightings=sightings, role=role)

@owner_bp.route("/mark-found/<int:pet_id>", methods=["POST"])
def mark_found(pet_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    pet = LostPet.query.filter_by(id=pet_id, owner_id=user_id).first_or_404()
    pet.status = "Found"
    db.session.commit()
    flash(f"Pet '{pet.name}' marked as Found!", "success")
    return redirect(url_for("owner.lost_found"))

# ===================== REVIEWS & SUBSCRIPTIONS =====================
@owner_bp.route("/reviews")
def reviews():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    sitter_reviews = SitterReview.query.join(Sitter).all()
    return render_template("owner_reviews.html", sitter_reviews=sitter_reviews, role=role)


@owner_bp.route("/subscription")
def subscription():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    # Example subscription plans
    subscriptions = [
        {"plan": "Basic", "price": 0, "status": "Active"},
        {"plan": "Premium", "price": 49, "status": "Inactive"},
        {"plan": "Gold", "price": 99, "status": "Inactive"}
    ]

    return render_template("owner_subscriptions.html", subscriptions=subscriptions, role=role)


# ---------------- FIND SITERS ---------------- #
@owner_bp.route("/sitters")
def find_sitters():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    sitters = Sitter.query.filter_by(verification_status="approved").all()
    sitter_data = []

    for sitter in sitters:
        availabilities = Availability.query.filter_by(sitter_id=sitter.id).all()
        for slot in availabilities:
            slot.start_dt = datetime.combine(slot.date, slot.start_time)
            slot.end_dt = datetime.combine(slot.date, slot.end_time)

            # check if slot is already booked
            slot.booking = Booking.query.filter(
                Booking.sitter_id == sitter.id,
                Booking.start_date < slot.end_dt,
                Booking.end_date > slot.start_dt
            ).first()

            # Format for display
            slot.start_dt_str = slot.start_dt.strftime("%Y-%m-%d %H:%M")
            slot.end_dt_str = slot.end_dt.strftime("%Y-%m-%d %H:%M")

        sitter_data.append({"sitter": sitter, "availabilities": availabilities})

    pets = Pet.query.filter_by(owner_id=user_id).all()
    return render_template("owner_sitters.html", sitter_data=sitter_data, pets=pets, role=role)


# ---------------- VIEW SITTER PROFILE ---------------- #
@owner_bp.route("/sitter/<int:sitter_id>")
def view_sitter_profile(sitter_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)
    reviews = SitterReview.query.filter_by(sitter_id=sitter_id).all()
    availabilities = Availability.query.filter_by(sitter_id=sitter.id).all()

    for slot in availabilities:
        slot.start_dt = datetime.combine(slot.date, slot.start_time)
        slot.end_dt = datetime.combine(slot.date, slot.end_time)
        slot.start_dt_str = slot.start_dt.strftime("%Y-%m-%d %H:%M")
        slot.end_dt_str = slot.end_dt.strftime("%Y-%m-%d %H:%M")

        slot.booking = Booking.query.filter(
            Booking.sitter_id == sitter.id,
            Booking.start_date < slot.end_dt,
            Booking.end_date > slot.start_dt
        ).first()

    return render_template(
        "owner_sitter_profile.html",
        sitter=sitter,
        reviews=reviews,
        availabilities=availabilities,
        role=role
    )


# ---------------- BOOK SITTER ---------------- #
@owner_bp.route("/book_sitter", methods=["POST"])
def book_sitter():
    user_id, role = check_login()
    if not user_id:
        flash("Please login first.", "danger")
        return redirect(url_for("auth.login"))

    try:
        sitter_id = int(request.form.get("sitter_id"))
        pet_id = int(request.form.get("pet_id"))
        start_dt = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        flash("Invalid booking data.", "danger")
        return redirect(url_for("owner.find_sitters"))

    # prevent overlapping bookings
    existing_booking = Booking.query.filter(
        Booking.sitter_id == sitter_id,
        Booking.start_date < end_dt,
        Booking.end_date > start_dt
    ).first()
    if existing_booking:
        flash("This slot is already booked!", "warning")
        return redirect(url_for("owner.find_sitters"))

    booking = Booking(
        pet_id=pet_id,
        sitter_id=sitter_id,
        start_date=start_dt,
        end_date=end_dt,
        status="pending"
    )
    db.session.add(booking)
    db.session.commit()
    flash("Booking request sent! Wait for sitter approval.", "success")
    return redirect(url_for("owner.find_sitters"))

# ---------------- OWNER MY BOOKINGS ---------------- #
@owner_bp.route("/my_bookings")
def my_bookings():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    bookings = Booking.query.join(Pet).filter(Pet.owner_id == user_id).all()
    return render_template("owner_my_bookings.html", bookings=bookings, role=role)

# ---------------- SHOW RATING FORM ---------------- #
@owner_bp.route("/rate_sitter/<int:sitter_id>")
def rate_sitter(sitter_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    sitter = Sitter.query.get_or_404(sitter_id)

    # Check if the owner already gave a rating
    existing_review = SitterReview.query.filter_by(
        sitter_id=sitter_id, owner_id=user_id
    ).first()

    current_rating = existing_review.rating if existing_review else 0
    current_review_text = existing_review.review_text if existing_review else ""

    return render_template(
        "owner_rate_sitter.html",
        sitter=sitter,
        current_rating=current_rating,
        current_review_text=current_review_text,
        role=role
    )


# ---------------- SUBMIT RATING ---------------- #
@owner_bp.route("/submit_rating/<int:sitter_id>", methods=["POST"])
def submit_rating(sitter_id):
    user_id, role = check_login()
    if not user_id:
        flash("Please login first.", "danger")
        return redirect(url_for("auth.login"))

    rating = request.form.get("rating")
    review_text = request.form.get("review", "").strip()

    if not rating or int(rating) not in [1,2,3,4,5]:
        flash("Please select a valid rating (1-5 stars).", "warning")
        return redirect(url_for("owner.rate_sitter", sitter_id=sitter_id))

    existing_review = SitterReview.query.filter_by(
        sitter_id=sitter_id, owner_id=user_id
    ).first()

    if existing_review:
        existing_review.rating = int(rating)
        existing_review.review_text = review_text
        flash("Your rating has been updated.", "success")
    else:
        new_review = SitterReview(
            sitter_id=sitter_id,
            owner_id=user_id,
            rating=int(rating),
            review_text=review_text
        )
        db.session.add(new_review)
        flash("Thanks for your feedback!", "success")

    db.session.commit()
    return redirect(url_for("owner.find_sitters"))

# ===================== SHOP =====================
@owner_bp.route("/shop")
def shop():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    products = Product.query.all()
    return render_template("owner_shop.html", products=products, role=role)

@owner_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)
    return render_template("owner_product_detail.html", product=product, role=role)
# ===================== CART & ORDERS =====================
@owner_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))

    if quantity > product.stock:
        flash("Quantity exceeds available stock!", "danger")
        return redirect(url_for("owner.product_detail", product_id=product_id))

    cart_item = Order.query.filter_by(buyer_id=user_id, product_id=product_id, status="cart").first()
    if cart_item:
        cart_item.quantity += quantity
        cart_item.total_price = cart_item.quantity * product.price
    else:
        cart_item = Order(
            buyer_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_price=quantity * product.price,
            status="cart"
        )
        db.session.add(cart_item)
    db.session.commit()
    flash("Added to cart successfully!", "success")
    return redirect(url_for("owner.cart"))

@owner_bp.route("/cart")
def cart():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    cart_items = Order.query.filter_by(buyer_id=user_id, status="cart").all()
    return render_template("cart.html", cart_items=cart_items, role=role)

@owner_bp.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    cart_item = Order.query.filter_by(buyer_id=user_id, product_id=product_id, status="cart").first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart!", "success")
    return redirect(url_for("owner.cart"))

@owner_bp.route("/checkout", methods=["POST"])
def checkout():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    cart_items = Order.query.filter_by(buyer_id=user_id, status="cart").all()
    if not cart_items:
        flash("Cart is empty!", "warning")
        return redirect(url_for("owner.cart"))

    for item in cart_items:
        item.status = "pending"  # or 'ordered'
        item.ordered_at = datetime.utcnow()
    db.session.commit()
    flash("Order placed successfully!", "success")
    return redirect(url_for("owner.orders"))

@owner_bp.route("/place-order/<int:product_id>", methods=["POST"])
def place_order(product_id):
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)

    order = Order(
        buyer_id=user_id,
        product_id=product.id,
        quantity=1,
        total_price=product.price,
        status="ordered"
    )
    db.session.add(order)
    db.session.commit()
    flash("Order placed successfully!", "success")
    return redirect(url_for("owner.orders"))


@owner_bp.route("/orders")
def orders():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    orders = Order.query.filter_by(buyer_id=user_id).filter(Order.status != "cart").all()
    return render_template("orders.html", orders=orders, role=role)
@owner_bp.route("/product_reviews", methods=["GET", "POST"])
def product_reviews():
    user_id, role = check_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    # Get all purchased products (exclude cart)
    purchased_orders = Order.query.filter(
        Order.buyer_id == user_id,
        Order.status != "cart"
    ).all()

    # Attach reviews for each product
    for order in purchased_orders:
        # All reviews for this product
        order.reviews = ProductReview.query.filter_by(product_id=order.product_id).all()
        # Current user's review (if exists)
        order.user_review = ProductReview.query.filter_by(
            product_id=order.product_id,
            user_id=user_id
        ).first()
        # Default: do not show form
        order.show_form = False

    # Handle POST from "Give Rating" button or review submission
    if request.method == "POST":
        action = request.form.get("action")
        product_id = int(request.form.get("product_id"))

        if action == "show_form":
            # Show form for the selected product only
            for order in purchased_orders:
                order.show_form = (order.product_id == product_id)

        elif action == "submit_review":
            rating = int(request.form.get("rating"))
            review_text = request.form.get("review", "").strip()

            existing_review = ProductReview.query.filter_by(
                product_id=product_id,
                user_id=user_id
            ).first()

            if existing_review:
                existing_review.rating = rating
                existing_review.review_text = review_text
                flash("Your review has been updated!", "success")
            else:
                new_review = ProductReview(
                    product_id=product_id,
                    user_id=user_id,
                    rating=rating,
                    review_text=review_text
                )
                db.session.add(new_review)
                flash("Thanks for your review!", "success")

            db.session.commit()
            return redirect(url_for("owner.product_reviews"))

    return render_template(
        "owner_product_reviews.html",
        orders=purchased_orders,
        role=role
    )