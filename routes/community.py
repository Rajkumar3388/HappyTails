from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.db import db
from models.lost_pet import LostPet
from models.sighting import Sighting
from models.user import User
from datetime import datetime

community_bp = Blueprint("community", __name__, url_prefix="/community")

# -----------------------------
# Community Feed / Dashboard
# -----------------------------
@community_bp.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    lost_pets = LostPet.query.filter_by(status="Lost").order_by(LostPet.created_at.desc()).all()

    # Count sightings for each lost pet
    for pet in lost_pets:
        pet.sightings_count = Sighting.query.filter_by(pet_id=pet.id, status="Pending").count()

    return render_template("dashboard_community.html", lost_pets=lost_pets)


# -----------------------------
# Report a Sighting
# -----------------------------
@community_bp.route("/report-sighting/<int:pet_id>", methods=["GET", "POST"])
def report_sighting(pet_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    pet = LostPet.query.get_or_404(pet_id)

    if pet.status == "Found":
        flash("This pet has already been found.", "warning")
        return redirect(url_for("community.feed"))

    if request.method == "POST":
        confidence = request.form.get("confidence")
        details = request.form.get("details")
        location = request.form.get("location")
        phone = request.form.get("phone")  # New field
        helper = User.query.get(session["user_id"])

        # Validate fields
        if not confidence or not details or not location or not phone:
            flash("All fields are required!", "danger")
            return redirect(url_for("community.report_sighting", pet_id=pet_id))

        try:
            new_sighting = Sighting(
                pet_id=pet.id,
                helper_name=helper.name,
                helper_phone=phone,        # Save helper's phone
                owner_id=pet.owner_id,
                confidence=int(confidence),
                details=details,
                location=location,
                status="Pending",
                created_at=datetime.utcnow()
            )
            db.session.add(new_sighting)
            db.session.commit()
            flash("✅ Sighting reported successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error reporting sighting: {str(e)}", "danger")

        return redirect(url_for("community.feed"))

    return render_template("report_sighting.html", pet=pet)


# -----------------------------
# View Sightings for a Pet
# -----------------------------
@community_bp.route("/pet-sightings/<int:pet_id>")
def pet_sightings(pet_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    pet = LostPet.query.get_or_404(pet_id)
    sightings = Sighting.query.filter_by(pet_id=pet.id).order_by(Sighting.created_at.desc()).all()
    return render_template("view_sightings.html", pet=pet, sightings=sightings)


# -----------------------------
# Owner Lost Pet Alerts
# -----------------------------
@community_bp.route("/owner-lost-pet-alerts")
def owner_lost_pet_alerts():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    owner_id = session["user_id"]

    alerts = LostPet.query.filter_by(owner_id=owner_id).order_by(LostPet.created_at.desc()).all()

    for pet in alerts:
        # Fetch pending sightings as a list
        pet.sightings = pet.sightings.filter_by(status="Pending") \
                                     .order_by(Sighting.created_at.desc()) \
                                     .all()
        pet.sightings_count = len(pet.sightings)

    return render_template("owner_lost_pet_alerts.html", alerts=alerts)
