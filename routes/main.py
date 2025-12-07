from flask import Blueprint, render_template, session, redirect, url_for, flash

main_bp = Blueprint("main", __name__)

# Landing Page
@main_bp.route("/")
def index():
    return render_template("index.html")


# Dashboard Route – Role Based
@main_bp.route("/dashboard")
def dashboard():
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.login"))

    # Get user role and name from session
    role = session.get("user_role", "guest")
    user_name = session.get("user_name", "Guest")

    # Map roles to dashboard templates
    template_map = {
        "owner": "dashboard_owner.html",
        "sitter": "dashboard_sitter.html",
        "seller": "dashboard_seller.html",
        "community": "dashboard_community.html",
        "admin": "dashboard_admin.html",
        "guest": "dashboard_guest.html"
    }

    # Select template based on role
    template = template_map.get(role, "dashboard_guest.html")

    # Render the correct dashboard template with user info
    return render_template(template, role=role.capitalize(), user_name=user_name)
