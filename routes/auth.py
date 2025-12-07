from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role", "owner")  # owner, sitter

        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        # Create user
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create Sitter row if role = sitter
        if role == "sitter":
            from models.sitter import Sitter
            sitter = Sitter(id=user.id, name=name, email=email)
            db.session.add(sitter)
            db.session.commit()

        flash("Registered successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_role"] = user.role
            session["user_name"] = user.name
            flash(f"Welcome {user.name}!", "success")

            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "sitter":
                return redirect(url_for("sitter.dashboard"))
            elif user.role == "owner":
                return redirect(url_for("owner.dashboard"))
            else:
                return redirect(url_for("main.dashboard"))

        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.login"))
# ---------------- FORGOT PASSWORD ----------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            # TODO: send reset email logic here
            flash("Password reset instructions sent to your email.", "success")
        else:
            flash("Email not found!", "danger")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")
